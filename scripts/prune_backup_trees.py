#!/usr/bin/env python3
"""prune_backup_trees.py -- real implementation of the retention policy
proposed in UMR-20260808-023802-1955 (Owner-approved report:
/opt/veridian/ai-os/reports/backup-tree-inventory-retention-proposal-UMR-20260808-023802-1955.md),
applied to both backup trees named in that report:

  Tree 1: /opt/veridian/backups/sqlite-daily
  Tree 2: /opt/veridian/ai-os/memory/backups

This is a DIFFERENT, more precise policy than /opt/veridian/repos/
veridian-scripts/prune_memory_backups.py's existing "keep N most-recent
verified" rule -- that script still owns its own systemd timer and its own
directory set (memory dir root + memory/backups, superboss-register.sqlite
only) and is left completely untouched by this script. This script
implements the exact same-day-dedup rule set (R1-R4) the report proposed,
across both trees, for every source database named there
(superboss-register.sqlite AND credit-ledger.sqlite).

POLICY (applies independently per tree, per source database -- see the
report's own Section 5 for the full derivation and worked numbers, not
re-derived here):

  R1 -- Never delete the live database, its -wal/-shm, or the single most
        recent backup of each source DB in each tree.
  R2 -- Same-day dedup: where a tree holds more than one full-DB snapshot
        of the SAME source database taken on the SAME UTC calendar day,
        keep only the most recent snapshot from that day (plus its own
        -wal/-shm sidecars); earlier same-day snapshots are removal
        candidates.
  R3 -- Never remove the sole backup of any calendar day, even if old.
  R4 -- Pre-condition: no deletion proceeds for a tree unless a FRESH
        read-only PRAGMA quick_check on that tree's implicated live
        database(s) (only the ones that actually own a removal candidate
        in that tree -- never a database with nothing pending deletion)
        returns 'ok' immediately beforehand. A failing check aborts THAT
        TREE's deletions only (prints why, deletes nothing there) -- it is
        never a crash, and never blocks an unrelated tree/database whose
        own check passed.

R1+R2+R3 collapse into one rule, implemented as one rule: for a given
source DB in a given tree, keep the group with the maximum mtime among
every group sharing its UTC calendar day. A day with only one group
trivially keeps it (R3). The overall most-recent group across all days is,
by construction, also its own day's maximum, so it is always kept too
(R1). Every other group in a day that holds more than one group is a
same-day dedup removal candidate (R2).

Dry-run is the default: prints the real plan (path/bytes/matched-rule) and
writes nothing. --execute is the ONLY way any deletion happens, and even
then only for trees whose R4 check(s) passed.

Usage:
  prune_backup_trees.py                          # dry run, both real trees, both real DBs
  prune_backup_trees.py --execute                # real deletions (gated per-tree by R4)
  prune_backup_trees.py --tree DIR [--tree DIR]  # override tree(s)
  prune_backup_trees.py --db NAME=LIVE_DB_PATH   # override/add a source DB (repeatable)

Exit codes: 0 = success (dry-run always; execute with no R4 abort). 1 = ran
with --execute and at least one tree's deletions were aborted by a failed
R4 check (a real, reported condition -- not a crash). 2 = usage error.
"""
import argparse
import json
import os
import sqlite3
import sys
import time
import urllib.parse
from datetime import datetime, timezone

# Env-overridable module-level defaults -- same testability convention
# prune_memory_backups.py and sqlite_daily_backup.py already established
# (VERIDIAN_PMB_*, SUPERBOSS_REGISTER_DB, ...): every real production caller
# gets the real, unchanged default; hermetic tests redirect these (or pass
# explicit `trees=`/`source_dbs=` to run() directly) without ever touching
# the real trees.
MEMORY_DIR = os.environ.get("VERIDIAN_PBT_MEMORY_DIR", "/opt/veridian/ai-os/memory")
SQLITE_DAILY_DIR = os.environ.get("VERIDIAN_PBT_SQLITE_DAILY_DIR", "/opt/veridian/backups/sqlite-daily")
MEMORY_BACKUPS_DIR = os.environ.get("VERIDIAN_PBT_MEMORY_BACKUPS_DIR", os.path.join(MEMORY_DIR, "backups"))

DEFAULT_TREES = [SQLITE_DAILY_DIR, MEMORY_BACKUPS_DIR]
DEFAULT_SOURCE_DBS = {
    "superboss-register.sqlite": os.path.join(MEMORY_DIR, "superboss-register.sqlite"),
    "credit-ledger.sqlite": os.path.join(MEMORY_DIR, "credit-ledger.sqlite"),
}

_COMPANION_SUFFIXES = ("-wal", "-shm")


def _protected_live_names(db_name):
    """Filenames that belong to the LIVE database itself -- never discovery
    candidates in any scanned tree, regardless of how unlikely it is for a
    live DB to sit inside one of the two real backup trees. Mirrors
    prune_memory_backups.py's LIVE_DB_PROTECTED convention."""
    return {db_name, db_name + "-wal", db_name + "-shm", db_name + ".writelock"}


def _companion_base(fname):
    """Returns (base_name, is_companion) -- strips a trailing -wal/-shm."""
    for suf in _COMPANION_SUFFIXES:
        if fname.endswith(suf):
            return fname[: -len(suf)], True
    return fname, False


def discover_groups_for_db(tree_dir, db_name):
    """Scan tree_dir for `<db_name>.*` files and group each backup's main
    file with its -wal/-shm companions found in the same directory. A
    group with no main_path (orphan sidecar with no matching main file) is
    real and included -- never verifiable as a standalone backup, but still
    accounted for under the same day/most-recent bookkeeping as everything
    else here."""
    groups = {}
    if not os.path.isdir(tree_dir):
        return []
    protected = _protected_live_names(db_name)
    prefix = db_name + "."
    for fname in sorted(os.listdir(tree_dir)):
        if fname in protected or not fname.startswith(prefix):
            continue
        full = os.path.join(tree_dir, fname)
        if not os.path.isfile(full):
            continue
        base, is_companion = _companion_base(fname)
        g = groups.setdefault(base, {
            "source_db": db_name, "dir": tree_dir, "base": base,
            "main_path": None, "companions": [],
        })
        if is_companion:
            g["companions"].append(full)
        else:
            g["main_path"] = full

    result = []
    for g in groups.values():
        if g["main_path"]:
            g["mtime"] = os.path.getmtime(g["main_path"])
        elif g["companions"]:
            g["mtime"] = max(os.path.getmtime(c) for c in g["companions"])
        else:
            continue
        g["day"] = datetime.fromtimestamp(g["mtime"], tz=timezone.utc).strftime("%Y-%m-%d")
        result.append(g)
    return result


def classify_groups(groups):
    """Tags each group in-place with decision ('keep'/'remove'), matched_rule
    ('R1'/'R2'/'R3'), and a human-readable rule_detail -- see module
    docstring for the collapsed R1+R2+R3 derivation. `groups` must all
    share the same (source_db, tree) -- callers pass one such set at a
    time."""
    if not groups:
        return groups
    overall_latest = max(groups, key=lambda g: g["mtime"])
    by_day = {}
    for g in groups:
        by_day.setdefault(g["day"], []).append(g)
    for day, day_groups in by_day.items():
        day_latest = max(day_groups, key=lambda g: g["mtime"])
        sole_day = len(day_groups) == 1
        for g in day_groups:
            if g is day_latest:
                g["decision"] = "keep"
                if g is overall_latest:
                    g["matched_rule"] = "R1"
                    g["rule_detail"] = "R1: single most recent backup for this source DB in this tree"
                elif sole_day:
                    g["matched_rule"] = "R3"
                    g["rule_detail"] = f"R3: sole backup of calendar day {day} -- never removed"
                else:
                    g["matched_rule"] = "R2"
                    g["rule_detail"] = f"R2: most recent same-day snapshot for {day} (dedup survivor)"
            else:
                g["decision"] = "remove"
                g["matched_rule"] = "R2"
                g["rule_detail"] = (
                    f"R2: redundant same-day snapshot for {day} -- "
                    f"{os.path.basename(day_latest['main_path'] or day_latest['base'])} is that day's survivor"
                )
    return groups


def check_live_db_integrity(path, retries=3, delay_s=1.0):
    """R4's own fresh, read-only PRAGMA quick_check against the live
    database at `path`. Retries a few times before declaring real failure
    -- the same transient-mid-write-snapshot guard sqlite_daily_backup.py's
    own check_integrity() uses. Never opens for write; a missing/zero-byte/
    unreadable/corrupt file is a real, honest False, never an exception
    escaping to the caller."""
    verdict = None
    last_err = None
    for attempt in range(retries):
        if not os.path.isfile(path) or os.path.getsize(path) == 0:
            return False, "live database file missing or zero-byte"
        try:
            uri = "file:" + urllib.parse.quote(os.path.abspath(path)) + "?mode=ro"
            conn = sqlite3.connect(uri, uri=True, timeout=10)
            try:
                rows = conn.execute("PRAGMA quick_check").fetchall()
                verdict = rows[0][0] if rows else "no quick_check output"
            finally:
                conn.close()
            if verdict == "ok":
                return True, verdict
        except sqlite3.Error as e:
            last_err = str(e)
            verdict = None
        if attempt < retries - 1:
            time.sleep(delay_s)
    return False, verdict or last_err or "unknown quick_check failure"


def group_paths(g):
    paths = list(g["companions"])
    if g["main_path"]:
        paths.append(g["main_path"])
    return paths


def group_size(g):
    return sum(os.path.getsize(p) for p in group_paths(g) if os.path.isfile(p))


def plan_tree(tree_dir, source_dbs):
    """Real, read-only plan for one tree -- discovers + classifies every
    group for every source DB, sorted newest-first. Returns (groups,
    dbs_needing_r4_check) where the latter is only the source DB names that
    actually own >=1 removal candidate in THIS tree (R4 only ever checks a
    live DB immediately before deleting one of its own backups -- an
    unrelated, healthy-or-not source DB with nothing pending deletion here
    is never gated)."""
    all_groups = []
    for name in source_dbs:
        groups = classify_groups(discover_groups_for_db(tree_dir, name))
        all_groups.extend(groups)
    all_groups.sort(key=lambda g: g["mtime"], reverse=True)
    dbs_needing_check = sorted({g["source_db"] for g in all_groups if g["decision"] == "remove"})
    return all_groups, dbs_needing_check


def run(trees, source_dbs, execute):
    """Real entry point (importable for tests). Never raises for the normal
    R4-abort case -- that is a real, reported per-tree outcome in the
    returned report, not an exception. dry-run (execute=False) makes zero
    filesystem writes, full stop; R4 checks still run and are still
    reported even in dry-run, so the printed plan honestly shows what a
    real --execute run would do."""
    report = {
        "mode": "execute" if execute else "dry-run",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "trees": [],
        "deleted_bytes": 0,
        "would_delete_bytes": 0,
        "any_r4_abort": False,
    }

    for tree_dir in trees:
        all_groups, dbs_needing_check = plan_tree(tree_dir, source_dbs)

        r4_checks = []
        r4_ok = True
        for db_name in dbs_needing_check:
            live_path = source_dbs[db_name]
            ok, verdict = check_live_db_integrity(live_path)
            r4_checks.append({"source_db": db_name, "live_db_path": live_path, "ok": ok, "verdict": verdict})
            if not ok:
                r4_ok = False

        tree_entry = {
            "tree_dir": tree_dir, "r4_checks": r4_checks, "r4_ok": r4_ok,
            "items": [], "deleted_bytes": 0, "would_delete_bytes": 0,
        }
        if execute and not r4_ok:
            report["any_r4_abort"] = True

        for g in all_groups:
            size = group_size(g)
            item = {
                "source_db": g["source_db"], "base": g["base"], "day": g["day"],
                "mtime_utc": datetime.fromtimestamp(g["mtime"], tz=timezone.utc).isoformat(),
                "main_path": g["main_path"], "companions": list(g["companions"]),
                "bytes": size, "decision": g["decision"],
                "matched_rule": g["matched_rule"], "rule_detail": g["rule_detail"],
            }
            if g["decision"] == "keep":
                item["action"] = "kept"
            elif not execute:
                item["action"] = "would-delete"
                tree_entry["would_delete_bytes"] += size
            elif not r4_ok:
                item["action"] = "blocked_by_r4"
                item["blocked_reason"] = (
                    "R4: live database integrity check failed for this tree's implicated source DB "
                    "-- ALL deletions aborted for this tree, nothing removed here."
                )
            else:
                deleted_paths = []
                for p in group_paths(g):
                    try:
                        os.remove(p)
                        deleted_paths.append(p)
                    except FileNotFoundError:
                        pass
                item["action"] = "deleted"
                item["deleted_paths"] = deleted_paths
                tree_entry["deleted_bytes"] += size
            tree_entry["items"].append(item)

        report["deleted_bytes"] += tree_entry["deleted_bytes"]
        report["would_delete_bytes"] += tree_entry["would_delete_bytes"]
        report["trees"].append(tree_entry)

    return report


def _parse_db_arg(spec):
    if "=" not in spec:
        raise ValueError(f"--db value {spec!r} must be NAME=LIVE_DB_PATH")
    name, path = spec.split("=", 1)
    if not name or not path:
        raise ValueError(f"--db value {spec!r} must be NAME=LIVE_DB_PATH")
    return name, path


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tree", action="append", default=None,
                     help="Backup tree directory to scan (repeatable). Default: both real trees "
                          f"named in UMR-20260808-023802-1955 ({', '.join(DEFAULT_TREES)}).")
    ap.add_argument("--db", action="append", default=None,
                     help="NAME=LIVE_DB_PATH source database to consider (repeatable). Default: "
                          "both real live DBs (superboss-register.sqlite, credit-ledger.sqlite).")
    ap.add_argument("--execute", action="store_true",
                     help="Apply real deletions (default: dry run -- prints the plan, deletes nothing).")
    return ap.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    trees = args.tree or DEFAULT_TREES
    if args.db:
        try:
            source_dbs = dict(_parse_db_arg(spec) for spec in args.db)
        except ValueError as e:
            print(json.dumps({"error": "BAD_ARGUMENT", "message": str(e)}, indent=2))
            return 2
    else:
        source_dbs = DEFAULT_SOURCE_DBS

    report = run(trees, source_dbs, args.execute)

    for tree_entry in report["trees"]:
        status = "OK" if tree_entry["r4_ok"] else "FAILED -- deletions aborted for this tree"
        print(f"=== tree: {tree_entry['tree_dir']}  (R4 {status}) ===")
        for check in tree_entry["r4_checks"]:
            mark = "ok" if check["ok"] else "FAILED"
            print(f"  R4 quick_check[{check['source_db']}]: {mark} ({check['verdict']}) "
                  f"live_db={check['live_db_path']}")
        for item in tree_entry["items"]:
            path = item["main_path"] or f"(orphan companions of {item['base']})"
            print(f"  {item['action']:14s} rule={item['matched_rule']:>2s} bytes={item['bytes']:>14,d} "
                  f"day={item['day']} path={path}")
        print(f"  -- would_delete_bytes={tree_entry['would_delete_bytes']:,} "
              f"deleted_bytes={tree_entry['deleted_bytes']:,}")

    print(json.dumps(report, indent=2, default=str))

    if args.execute and report["any_r4_abort"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
