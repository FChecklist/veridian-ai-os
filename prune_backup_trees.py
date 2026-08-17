#!/usr/bin/env python3
"""
prune_backup_trees.py -- implement backup tree retention policy for
/opt/veridian/backups/sqlite-daily and /opt/veridian/ai-os/memory/backups

Governance: UMR-20260808-023802-1955 (backup-tree-inventory-retention-proposal)
Owner-approved 2026-08-17.

Implements rules R1-R4 from the governing report, section 5:

  R1: Never delete the live database, its -wal/-shm sidecars, or the single
      most recent backup of each source DB in each tree.
  R2: Same-day dedup -- if a tree holds more than one full-DB snapshot of the
      SAME source database on the SAME UTC calendar day, keep only the most
      recent from that day (plus its own -wal/-shm sidecars); earlier same-day
      snapshots are removal candidates.
  R3: Never remove the sole backup of any calendar day, even if old.
  R4: Pre-condition -- no deletion proceeds unless a fresh read-only PRAGMA
      integrity_check/quick_check on the live source database returns ok
      immediately beforehand; abort (skip that tree's deletions, do not crash)
      if it does not.

SAFETY CONTRACT: mirrored from reconcile_stale_running_workers.py pattern:
  - Dry run is the DEFAULT with no flags -- prints exactly what would be
    removed (path, bytes, which rule matched) and the real R4 integrity-check
    result, writes zero files, deletes nothing.
  - Add an explicit --execute flag that is the ONLY way any deletion happens,
    and even then only after R4 passes fresh at execute time.

Usage:
  python3 prune_backup_trees.py             # dry run (default, no writes)
  python3 prune_backup_trees.py --execute   # real writes
  python3 prune_backup_trees.py --tree TREE # prune only TREE
  python3 prune_backup_trees.py --live-db PATH --live-db-dir DIR  # override paths (testing)

Exit codes: 0 success (dry-run or real), 1 integrity check failed (refused,
nothing touched), 2 bad arguments.
"""
import argparse
import json
import os
import re
import sqlite3
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

# Real backup tree locations
TREES = {
    "sqlite-daily": "/opt/veridian/backups/sqlite-daily",
    "memory-backups": "/opt/veridian/ai-os/memory/backups",
}

# Live database locations (these MUST NOT be deleted)
# Both trees back up the SAME live database
LIVE_DBS = {
    "sqlite-daily": "/opt/veridian/ai-os/memory/superboss-register.sqlite",
    "memory-backups": "/opt/veridian/ai-os/memory/superboss-register.sqlite",
}

# Env overrides for testing
TREE_SQLITE_DAILY = os.environ.get("VERIDIAN_PTB_TREE_SQLITE_DAILY", TREES["sqlite-daily"])
TREE_MEMORY_BACKUPS = os.environ.get("VERIDIAN_PTB_TREE_MEMORY_BACKUPS", TREES["memory-backups"])
LIVE_DB_SQLITE_DAILY = os.environ.get("VERIDIAN_PTB_LIVE_DB_SQLITE_DAILY", LIVE_DBS["sqlite-daily"])
LIVE_DB_MEMORY_BACKUPS = os.environ.get("VERIDIAN_PTB_LIVE_DB_MEMORY_BACKUPS", LIVE_DBS["memory-backups"])

# Pattern to extract backup info from filenames
# Expects: <db_name>.<date_or_timestamp>[.suffix]
# Examples:
#   superboss-register.sqlite.20260806.bak
#   superboss-register.sqlite.20260806-100057Z-fresh.bak
#   credit-ledger.sqlite.20260725.bak
#   superboss-register.sqlite.pre-fullfile-backup-20260806T193316Z
BACKUP_PATTERN = re.compile(
    r"^([a-z0-9\-]+\.sqlite)(\.(\d{8})[a-zA-Z0-9\-\.T:Z]*)?(?:\.bak|-wal|-shm)?$"
)

COMPANION_SUFFIXES = ("-wal", "-shm")


def extract_backup_info(filename):
    """Parse filename and extract (db_base, date, timestamp_str, is_companion).

    Returns: (db_base, utc_date, full_ts_str, is_companion) or (None, None, None, None)
    where:
      - db_base: the base database name (e.g., 'superboss-register.sqlite')
      - utc_date: ISO date string (YYYYMMDD), or None if no date found
      - full_ts_str: full timestamp portion including any time markers
      - is_companion: True if this is a -wal/-shm file
    """
    # Check if it's a companion file
    is_companion = False
    base_fname = filename
    for suf in COMPANION_SUFFIXES:
        if filename.endswith(suf):
            is_companion = True
            base_fname = filename[: -len(suf)]
            break

    # Look for a YYYYMMDD date pattern anywhere in the filename
    # This handles both .sqlite.YYYYMMDD.* and .sqlite.prefix-YYYYMMDD* formats
    date_match = re.search(r'(\d{8})', base_fname)
    if not date_match:
        return None, None, None, is_companion

    utc_date = date_match.group(1)

    # Extract the db_base (everything up to and including .sqlite)
    # Pattern: <db_name>.sqlite followed by date info
    prefix_match = re.match(r'^([a-z0-9\-]+\.sqlite)', base_fname)
    if not prefix_match:
        return None, None, None, is_companion

    db_base = prefix_match.group(1)

    # Extract the timestamp portion (everything after .sqlite)
    ts_part_start = len(db_base)
    if ts_part_start >= len(base_fname):
        ts_str = ""
    else:
        ts_str = base_fname[ts_part_start:].lstrip(".")

    return db_base, utc_date, ts_str, is_companion


def real_integrity_check(path, timeout=30):
    """Check if a database passes PRAGMA integrity_check.

    Returns True iff PRAGMA integrity_check returns exactly [('ok',)].
    Returns False for any error, missing file, zero bytes, not a database, etc.
    """
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        return False
    uri = "file:" + urllib.parse.quote(os.path.abspath(path)) + "?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True, timeout=timeout)
        try:
            rows = conn.execute("PRAGMA integrity_check").fetchall()
        finally:
            conn.close()
        return len(rows) == 1 and rows[0][0] == "ok"
    except Exception:
        return False


def discover_backups(tree_path):
    """Scan tree_path for backup files.

    Returns a list of dicts:
    {
      'path': full path,
      'filename': basename,
      'db_base': database base name,
      'utc_date': YYYYMMDD string,
      'ts_str': full timestamp string,
      'is_companion': bool,
      'size': file size in bytes,
      'mtime': modification time
    }
    """
    backups = []
    if not os.path.isdir(tree_path):
        return backups

    for fname in sorted(os.listdir(tree_path)):
        full_path = os.path.join(tree_path, fname)
        if not os.path.isfile(full_path):
            continue

        db_base, utc_date, ts_str, is_companion = extract_backup_info(fname)
        if db_base is None:
            continue

        backups.append({
            'path': full_path,
            'filename': fname,
            'db_base': db_base,
            'utc_date': utc_date,
            'ts_str': ts_str,
            'is_companion': is_companion,
            'size': os.path.getsize(full_path),
            'mtime': os.path.getmtime(full_path),
        })

    return backups


def group_backups(backups):
    """Group backups by (db_base, utc_date, ts_str), bundling companions.

    Returns dict: {group_key: {'main': backup_dict, 'companions': [backup_dicts]}
    where group_key = (db_base, utc_date, ts_str)
    """
    groups = defaultdict(lambda: {'main': None, 'companions': []})

    for backup in backups:
        key = (backup['db_base'], backup['utc_date'], backup['ts_str'])
        if backup['is_companion']:
            groups[key]['companions'].append(backup)
        else:
            groups[key]['main'] = backup

    return groups


def identify_removal_candidates(tree_path, live_db_path, groups):
    """Apply R1-R4 rules to identify which backups should be removed.

    Returns: {
      'candidate_groups': [{'reason': str, 'main': backup_dict, 'companions': []}],
      'keep_groups': [{...}],
      'integrity_ok': bool,
      'integrity_error': str or None,
    }
    """
    result = {
        'candidate_groups': [],
        'keep_groups': [],
        'integrity_ok': None,
        'integrity_error': None,
    }

    # R4: Check live DB integrity
    if not os.path.exists(live_db_path):
        result['integrity_ok'] = None
        result['integrity_error'] = f"Live DB not found: {live_db_path}"
        return result

    integrity_ok = real_integrity_check(live_db_path)
    result['integrity_ok'] = integrity_ok
    if not integrity_ok:
        result['integrity_error'] = f"Live DB failed integrity check: {live_db_path}"
        return result

    # Get live DB name to protect it
    live_db_name = os.path.basename(live_db_path)

    # Group backups by database
    by_db = defaultdict(list)
    for (db_base, utc_date, ts_str), group in groups.items():
        by_db[db_base].append(((db_base, utc_date, ts_str), group))

    # R1: Keep most recent backup of each source DB
    most_recent_per_db = {}
    for db_base, groups_for_db in by_db.items():
        # Sort by mtime, most recent first
        sorted_groups = sorted(
            groups_for_db,
            key=lambda x: x[1]['main']['mtime'] if x[1]['main'] else 0,
            reverse=True
        )
        if sorted_groups:
            most_recent_per_db[db_base] = sorted_groups[0][0]  # The key tuple

    # R3: Never remove the sole backup of any calendar day
    sole_backup_per_day = {}
    for db_base, groups_for_db in by_db.items():
        by_date = defaultdict(list)
        for key, group in groups_for_db:
            by_date[key[1]].append(key)  # key[1] is utc_date

        for date, keys_on_date in by_date.items():
            if len(keys_on_date) == 1:
                sole_backup_per_day[keys_on_date[0]] = date

    # R2 + R1: Apply rules
    for (db_base, utc_date, ts_str), group in groups.items():
        key = (db_base, utc_date, ts_str)

        # R1: Never delete the most recent backup of each DB
        if key == most_recent_per_db.get(db_base):
            result['keep_groups'].append((key, group, "R1_most_recent_per_db"))
            continue

        # R3: Never delete the sole backup of any calendar day
        if key in sole_backup_per_day:
            result['keep_groups'].append((key, group, "R3_sole_backup_per_day"))
            continue

        # R2: Same-day dedup - keep only most recent per (db_base, date)
        # Find all backups of this DB on this date
        same_day_group = [
            ((db, d, ts), g) for (db, d, ts), g in groups.items()
            if db == db_base and d == utc_date
        ]

        if len(same_day_group) > 1:
            # Multiple backups same day - keep most recent
            most_recent = max(
                same_day_group,
                key=lambda x: x[1]['main']['mtime'] if x[1]['main'] else 0
            )
            if key == most_recent[0]:
                result['keep_groups'].append((key, group, "R2_most_recent_same_day"))
            else:
                result['candidate_groups'].append({
                    'key': key,
                    'main': group['main'],
                    'companions': group['companions'],
                    'reason': 'R2_same_day_dedup'
                })
        else:
            # Single backup on this day, but not the most recent overall
            result['keep_groups'].append((key, group, "default_keep"))

    return result


def plan_prune(tree_name, tree_path, live_db_path):
    """Develop the prune plan for a single tree.

    Returns: {
      'tree': tree_name,
      'tree_path': tree_path,
      'live_db': live_db_path,
      'candidates': [...],
      'integrity_ok': bool or None,
      'integrity_error': str or None,
    }
    """
    backups = discover_backups(tree_path)
    groups = group_backups(backups)

    result = identify_removal_candidates(tree_path, live_db_path, groups)

    plan = {
        'tree': tree_name,
        'tree_path': tree_path,
        'live_db': live_db_path,
        'integrity_ok': result['integrity_ok'],
        'integrity_error': result['integrity_error'],
        'candidates': [],
        'total_candidate_bytes': 0,
    }

    for candidate in result['candidate_groups']:
        main = candidate['main']
        companions = candidate['companions']
        total_size = (main['size'] if main else 0) + sum(c['size'] for c in companions)

        files = []
        if main:
            files.append({
                'path': main['path'],
                'size': main['size'],
                'type': 'main'
            })
        for comp in companions:
            files.append({
                'path': comp['path'],
                'size': comp['size'],
                'type': 'companion'
            })

        plan['candidates'].append({
            'reason': candidate['reason'],
            'db_base': candidate['main']['db_base'] if candidate['main'] else None,
            'utc_date': candidate['main']['utc_date'] if candidate['main'] else None,
            'ts_str': candidate['main']['ts_str'] if candidate['main'] else None,
            'files': files,
            'total_bytes': total_size,
        })
        plan['total_candidate_bytes'] += total_size

    # Sort by mtime descending
    if plan['candidates']:
        plan['candidates'].sort(
            key=lambda c: max(
                (os.path.getmtime(f['path']) for f in c['files']),
                default=0
            ),
            reverse=True
        )

    return plan


def execute_prune(plan):
    """Execute deletion for a prune plan.

    Returns count of files deleted.
    """
    if plan['integrity_error']:
        return 0

    deleted_count = 0
    for candidate in plan['candidates']:
        for file_info in candidate['files']:
            try:
                os.remove(file_info['path'])
                deleted_count += 1
            except FileNotFoundError:
                pass

    return deleted_count


def format_bytes(num_bytes):
    """Format bytes to human-readable string."""
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.2f}{unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f}PiB"


def print_plan(plan):
    """Pretty-print a prune plan."""
    print(f"\n{'='*80}")
    print(f"Tree: {plan['tree']}")
    print(f"Path: {plan['tree_path']}")
    print(f"Live DB: {plan['live_db']}")
    print(f"{'='*80}")

    if plan['integrity_error']:
        print(f"ERROR: {plan['integrity_error']}")
        print("SKIPPING THIS TREE (R4 pre-condition failed)")
        return

    if plan['integrity_ok']:
        print("✓ Live DB integrity check PASSED")
    else:
        print("✗ Live DB integrity check FAILED")
        print("SKIPPING THIS TREE")
        return

    if not plan['candidates']:
        print("No removal candidates found.")
        return

    print(f"\nRemoval candidates ({len(plan['candidates'])} groups, "
          f"{format_bytes(plan['total_candidate_bytes'])} total):")
    print()

    for i, candidate in enumerate(plan['candidates'], 1):
        print(f"{i}. {candidate['reason']}")
        print(f"   DB: {candidate['db_base']}")
        print(f"   Date: {candidate['utc_date']}")
        print(f"   Time: {candidate['ts_str']}")
        print(f"   Total: {format_bytes(candidate['total_bytes'])}")
        for file_info in candidate['files']:
            ftype = "  " if file_info['type'] == 'main' else "  +"
            fname = os.path.basename(file_info['path'])
            print(f"     {ftype} {fname} ({format_bytes(file_info['size'])})")
        print()


def run(trees_to_run, execute=False, live_db_overrides=None):
    """Main prune logic.

    Returns list of plans.
    """
    if live_db_overrides is None:
        live_db_overrides = {}

    plans = []
    total_bytes = 0
    total_files = 0
    total_errors = 0

    trees_config = {
        "sqlite-daily": (TREE_SQLITE_DAILY, live_db_overrides.get("sqlite-daily", LIVE_DB_SQLITE_DAILY)),
        "memory-backups": (TREE_MEMORY_BACKUPS, live_db_overrides.get("memory-backups", LIVE_DB_MEMORY_BACKUPS)),
    }

    for tree_name in trees_to_run:
        if tree_name not in trees_config:
            print(f"ERROR: Unknown tree: {tree_name}", file=sys.stderr)
            total_errors += 1
            continue

        tree_path, live_db_path = trees_config[tree_name]
        plan = plan_prune(tree_name, tree_path, live_db_path)
        plans.append(plan)

        print_plan(plan)

        if not plan['integrity_error'] and plan['integrity_ok']:
            total_bytes += plan['total_candidate_bytes']
            for candidate in plan['candidates']:
                total_files += len(candidate['files'])

            if execute:
                deleted_count = execute_prune(plan)
                print(f"✓ Deleted {deleted_count} files")

    print(f"\n{'='*80}")
    if execute:
        print(f"EXECUTED: {total_files} files, {format_bytes(total_bytes)}")
    else:
        print(f"DRY RUN: Would remove {total_files} files, {format_bytes(total_bytes)}")

    if total_errors > 0:
        print(f"Errors: {total_errors} trees", file=sys.stderr)

    print(f"{'='*80}\n")

    return plans


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Prune backup trees following R1-R4 retention policy "
                    "(UMR-20260808-023802-1955)")
    ap.add_argument(
        "--execute",
        action="store_true",
        help="Execute deletion (default is dry-run only)"
    )
    ap.add_argument(
        "--tree",
        choices=["sqlite-daily", "memory-backups"],
        action="append",
        dest="trees",
        help="Prune only specified tree (repeatable). Default: both trees."
    )
    ap.add_argument(
        "--live-db-sqlite-daily",
        help="Override live DB path for sqlite-daily tree (testing only)"
    )
    ap.add_argument(
        "--live-db-memory-backups",
        help="Override live DB path for memory-backups tree (testing only)"
    )

    args = ap.parse_args(argv)

    trees_to_run = args.trees or ["sqlite-daily", "memory-backups"]

    live_db_overrides = {}
    if args.live_db_sqlite_daily:
        live_db_overrides["sqlite-daily"] = args.live_db_sqlite_daily
    if args.live_db_memory_backups:
        live_db_overrides["memory-backups"] = args.live_db_memory_backups

    try:
        plans = run(trees_to_run, execute=args.execute, live_db_overrides=live_db_overrides)

        # Determine exit code
        has_errors = any(p.get('integrity_error') for p in plans)
        return 1 if has_errors else 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
