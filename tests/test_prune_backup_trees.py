#!/usr/bin/env python3
"""Real tests for scripts/prune_backup_trees.py (governed by UMR-20260818-025834-fa54,
implementing UMR-20260808-023802-1955's R1-R4 retention policy for real).

Every test builds real sqlite files (via sqlite3.connect + real DDL) in a real tempdir
and drives the module's real functions (run()/main()) against those real files -- no
mocking of sqlite3 or the filesystem. Imports the module via the same importlib-by-
file-path pattern veridian-scripts' own test suite uses (test_prune_memory_backups.py,
test_reconcile_stale_running_workers.py) for hyphen/underscore-safe, always-fresh-copy
loading.

NEVER touches the two real backup trees (/opt/veridian/backups/sqlite-daily,
/opt/veridian/ai-os/memory/backups) or the real live databases -- every test passes
explicit tempdir `trees=`/`source_dbs=` to run(), or explicit --tree/--db/--live-db
CLI overrides for the subprocess-level tests.
"""
import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(REPO_ROOT, "scripts", "prune_backup_trees.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("prune_backup_trees_test", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_valid_db(path):
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT)")
    conn.execute("INSERT INTO t (v) VALUES ('x')")
    conn.commit()
    conn.close()


def _make_corrupt_file(path, content=b"not a real sqlite file at all"):
    with open(path, "wb") as f:
        f.write(content)


def _touch_mtime(path, ts):
    os.utime(path, (ts, ts))


def _day_ts(base_ts, day_offset, hour_offset_s=0):
    """A timestamp `day_offset` whole days before base_ts, at a real, distinct
    hour-offset within that UTC day -- deliberately far from any day boundary so a
    freshly-run test never flakes near UTC midnight."""
    DAY = 86400
    return (int(base_ts) // DAY) * DAY + 12 * 3600 - day_offset * DAY + hour_offset_s


# ---------------------------------------------------------------------------
# check_live_db_integrity
# ---------------------------------------------------------------------------

def test_integrity_check_true_on_real_db():
    m = _load_module()
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "real.sqlite")
        _make_valid_db(p)
        ok, verdict = m.check_live_db_integrity(p, retries=1)
        assert ok is True
        assert verdict == "ok"


def test_integrity_check_false_on_corrupt_file():
    m = _load_module()
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "corrupt.sqlite")
        _make_corrupt_file(p)
        ok, verdict = m.check_live_db_integrity(p, retries=1)
        assert ok is False


def test_integrity_check_false_on_missing_file():
    m = _load_module()
    with tempfile.TemporaryDirectory() as d:
        ok, verdict = m.check_live_db_integrity(os.path.join(d, "nope.sqlite"), retries=1)
        assert ok is False
        assert "missing" in verdict


# ---------------------------------------------------------------------------
# R1 -- single most recent backup per source DB per tree is always kept
# ---------------------------------------------------------------------------

def test_r1_keeps_the_single_most_recent_backup_overall():
    m = _load_module()
    now = time.time()
    with tempfile.TemporaryDirectory() as tree, tempfile.TemporaryDirectory() as mem:
        live = os.path.join(mem, "superboss-register.sqlite")
        _make_valid_db(live)

        # Day -2: two same-day dupes (R2 case, dup_old removed, dup_new survives).
        dup_old = os.path.join(tree, "superboss-register.sqlite.20260805-a.bak")
        dup_new = os.path.join(tree, "superboss-register.sqlite.20260805-b.bak")
        _make_valid_db(dup_old); _touch_mtime(dup_old, _day_ts(now, 2, 0))
        _make_valid_db(dup_new); _touch_mtime(dup_new, _day_ts(now, 2, 3600))

        # Day 0 (most recent day, sole backup that day): the real R1 case.
        newest = os.path.join(tree, "superboss-register.sqlite.20260807.bak")
        _make_valid_db(newest); _touch_mtime(newest, _day_ts(now, 0, 0))

        report = m.run([tree], {"superboss-register.sqlite": live}, execute=False)
        items = {os.path.basename(i["main_path"]): i for i in report["trees"][0]["items"]}

        assert items[os.path.basename(newest)]["matched_rule"] == "R1"
        assert items[os.path.basename(newest)]["decision"] == "keep"
        assert items[os.path.basename(dup_new)]["matched_rule"] == "R2"
        assert items[os.path.basename(dup_new)]["decision"] == "keep"
        assert items[os.path.basename(dup_old)]["matched_rule"] == "R2"
        assert items[os.path.basename(dup_old)]["decision"] == "remove"


# ---------------------------------------------------------------------------
# R2 -- same-day dedup
# ---------------------------------------------------------------------------

def test_r2_same_day_dedup_keeps_only_most_recent_same_day_snapshot():
    m = _load_module()
    now = time.time()
    with tempfile.TemporaryDirectory() as tree, tempfile.TemporaryDirectory() as mem:
        live = os.path.join(mem, "superboss-register.sqlite")
        _make_valid_db(live)

        paths = []
        for i, hr in enumerate([0, 3600, 7200, 10800, 14400]):
            p = os.path.join(tree, f"superboss-register.sqlite.20260806-{i}.bak")
            _make_valid_db(p)
            _touch_mtime(p, _day_ts(now, 1, hr))
            paths.append(p)
        survivor = paths[-1]  # latest hour offset == most recent that day

        report = m.run([tree], {"superboss-register.sqlite": live}, execute=False)
        items = {i["main_path"]: i for i in report["trees"][0]["items"]}

        assert items[survivor]["decision"] == "keep"
        for p in paths[:-1]:
            assert items[p]["decision"] == "remove"
            assert items[p]["matched_rule"] == "R2"
        assert report["trees"][0]["would_delete_bytes"] > 0


def test_r2_execute_actually_deletes_the_redundant_same_day_copies():
    m = _load_module()
    now = time.time()
    with tempfile.TemporaryDirectory() as tree, tempfile.TemporaryDirectory() as mem:
        live = os.path.join(mem, "superboss-register.sqlite")
        _make_valid_db(live)

        old = os.path.join(tree, "superboss-register.sqlite.same-day-old.bak")
        new = os.path.join(tree, "superboss-register.sqlite.same-day-new.bak")
        _make_valid_db(old); _touch_mtime(old, _day_ts(now, 0, 0))
        _make_valid_db(new); _touch_mtime(new, _day_ts(now, 0, 3600))

        report = m.run([tree], {"superboss-register.sqlite": live}, execute=True)

        assert not os.path.isfile(old), "R2 removal candidate must actually be deleted under --execute"
        assert os.path.isfile(new), "R1/R2 survivor must never be deleted"
        assert report["trees"][0]["deleted_bytes"] > 0
        assert report["any_r4_abort"] is False


# ---------------------------------------------------------------------------
# R3 -- sole backup of any calendar day is never removed
# ---------------------------------------------------------------------------

def test_r3_never_removes_the_sole_backup_of_a_calendar_day():
    m = _load_module()
    now = time.time()
    with tempfile.TemporaryDirectory() as tree, tempfile.TemporaryDirectory() as mem:
        live = os.path.join(mem, "superboss-register.sqlite")
        _make_valid_db(live)

        # 5 distinct days, one lone backup each -- none should ever be a removal
        # candidate, no matter how old, including the oldest.
        paths = []
        for day in range(5):
            p = os.path.join(tree, f"superboss-register.sqlite.day{day}.bak")
            _make_valid_db(p)
            _touch_mtime(p, _day_ts(now, day))
            paths.append(p)

        report = m.run([tree], {"superboss-register.sqlite": live}, execute=True)

        for p in paths:
            assert os.path.isfile(p), f"{p} is the sole backup of its day -- R3 must keep it"
        items = {i["main_path"]: i for i in report["trees"][0]["items"]}
        for p in paths:
            assert items[p]["decision"] == "keep"
            assert items[p]["matched_rule"] in ("R1", "R3")
        # Exactly one (the newest day) is R1; the rest are R3.
        rules = sorted(items[p]["matched_rule"] for p in paths)
        assert rules == ["R1", "R3", "R3", "R3", "R3"]


# ---------------------------------------------------------------------------
# R4 -- fresh integrity check gates deletion; abort is per-tree, not a crash
# ---------------------------------------------------------------------------

def test_r4_aborts_deletions_for_a_tree_when_live_db_integrity_check_fails():
    m = _load_module()
    now = time.time()
    with tempfile.TemporaryDirectory() as tree, tempfile.TemporaryDirectory() as mem:
        live = os.path.join(mem, "superboss-register.sqlite")
        _make_corrupt_file(live)  # live DB fails integrity_check

        old = os.path.join(tree, "superboss-register.sqlite.a.bak")
        new = os.path.join(tree, "superboss-register.sqlite.b.bak")
        _make_valid_db(old); _touch_mtime(old, _day_ts(now, 0, 0))
        _make_valid_db(new); _touch_mtime(new, _day_ts(now, 0, 3600))

        report = m.run([tree], {"superboss-register.sqlite": live}, execute=True)

        assert report["any_r4_abort"] is True
        assert report["trees"][0]["r4_ok"] is False
        assert os.path.isfile(old), "R4 must abort this tree's deletions -- nothing removed"
        assert os.path.isfile(new)
        items = {i["main_path"]: i for i in report["trees"][0]["items"]}
        assert items[old]["action"] == "blocked_by_r4"
        assert report["trees"][0]["deleted_bytes"] == 0


def test_r4_abort_in_one_tree_does_not_block_a_healthy_tree():
    """The report says 'abort THAT tree's deletions' -- a real, per-tree outcome, not a
    global crash or a global refusal. A second tree with a healthy live DB must still
    get its real deletions applied in the same run."""
    m = _load_module()
    now = time.time()
    with tempfile.TemporaryDirectory() as sick_tree, \
         tempfile.TemporaryDirectory() as healthy_tree, \
         tempfile.TemporaryDirectory() as mem:
        sick_live = os.path.join(mem, "superboss-register.sqlite")
        _make_corrupt_file(sick_live)
        healthy_live = os.path.join(mem, "credit-ledger.sqlite")
        _make_valid_db(healthy_live)

        sick_old = os.path.join(sick_tree, "superboss-register.sqlite.a.bak")
        sick_new = os.path.join(sick_tree, "superboss-register.sqlite.b.bak")
        _make_valid_db(sick_old); _touch_mtime(sick_old, _day_ts(now, 0, 0))
        _make_valid_db(sick_new); _touch_mtime(sick_new, _day_ts(now, 0, 3600))

        healthy_old = os.path.join(healthy_tree, "credit-ledger.sqlite.a.bak")
        healthy_new = os.path.join(healthy_tree, "credit-ledger.sqlite.b.bak")
        _make_valid_db(healthy_old); _touch_mtime(healthy_old, _day_ts(now, 0, 0))
        _make_valid_db(healthy_new); _touch_mtime(healthy_new, _day_ts(now, 0, 3600))

        source_dbs = {"superboss-register.sqlite": sick_live, "credit-ledger.sqlite": healthy_live}
        report = m.run([sick_tree, healthy_tree], source_dbs, execute=True)

        assert report["any_r4_abort"] is True
        assert os.path.isfile(sick_old), "sick tree's deletions must be aborted"
        assert not os.path.isfile(healthy_old), "healthy tree's real dedup deletion must still proceed"
        assert os.path.isfile(healthy_new)


def test_r4_only_checks_a_source_db_that_actually_has_a_removal_candidate():
    """An unrelated source DB with nothing pending deletion in this tree must never be
    integrity-checked or allowed to block a tree's real, unrelated deletions."""
    m = _load_module()
    now = time.time()
    with tempfile.TemporaryDirectory() as tree, tempfile.TemporaryDirectory() as mem:
        sick_live = os.path.join(mem, "credit-ledger.sqlite")
        _make_corrupt_file(sick_live)  # unhealthy, but owns zero backups in `tree`
        healthy_live = os.path.join(mem, "superboss-register.sqlite")
        _make_valid_db(healthy_live)

        old = os.path.join(tree, "superboss-register.sqlite.a.bak")
        new = os.path.join(tree, "superboss-register.sqlite.b.bak")
        _make_valid_db(old); _touch_mtime(old, _day_ts(now, 0, 0))
        _make_valid_db(new); _touch_mtime(new, _day_ts(now, 0, 3600))

        source_dbs = {"superboss-register.sqlite": healthy_live, "credit-ledger.sqlite": sick_live}
        report = m.run([tree], source_dbs, execute=True)

        checked = {c["source_db"] for c in report["trees"][0]["r4_checks"]}
        assert checked == {"superboss-register.sqlite"}
        assert report["any_r4_abort"] is False
        assert not os.path.isfile(old), "real deletion must proceed -- the unhealthy DB owns nothing here"


# ---------------------------------------------------------------------------
# dry-run has zero side effects
# ---------------------------------------------------------------------------

def test_dry_run_has_zero_side_effects():
    m = _load_module()
    now = time.time()
    with tempfile.TemporaryDirectory() as tree, tempfile.TemporaryDirectory() as mem:
        live = os.path.join(mem, "superboss-register.sqlite")
        _make_valid_db(live)

        paths = []
        for i, hr in enumerate([0, 3600, 7200]):
            p = os.path.join(tree, f"superboss-register.sqlite.dryrun-{i}.bak")
            _make_valid_db(p)
            _touch_mtime(p, _day_ts(now, 0, hr))
            paths.append(p)

        before = {p: (os.path.getsize(p), os.path.getmtime(p)) for p in paths}
        before_listing = sorted(os.listdir(tree))

        report = m.run([tree], {"superboss-register.sqlite": live}, execute=False)

        assert report["mode"] == "dry-run"
        after_listing = sorted(os.listdir(tree))
        assert after_listing == before_listing, "dry-run must not create, remove, or rename any file"
        for p in paths:
            assert (os.path.getsize(p), os.path.getmtime(p)) == before[p], "dry-run must not touch file contents/mtime"
        # The live DB itself must remain untouched and still verify.
        assert m.check_live_db_integrity(live, retries=1)[0] is True
        # Even a corrupt live DB must produce zero side effects in dry-run.
        _make_corrupt_file(live)
        report2 = m.run([tree], {"superboss-register.sqlite": live}, execute=False)
        assert report2["trees"][0]["r4_ok"] is False
        after_listing2 = sorted(os.listdir(tree))
        assert after_listing2 == before_listing


# ---------------------------------------------------------------------------
# -wal/-shm companions grouped and deleted together
# ---------------------------------------------------------------------------

def test_wal_shm_companions_grouped_and_deleted_together():
    m = _load_module()
    now = time.time()
    with tempfile.TemporaryDirectory() as tree, tempfile.TemporaryDirectory() as mem:
        live = os.path.join(mem, "superboss-register.sqlite")
        _make_valid_db(live)

        old_base = os.path.join(tree, "superboss-register.sqlite.20260806-pre-recover.bak")
        _make_valid_db(old_base)
        _touch_mtime(old_base, _day_ts(now, 0, 0))
        old_wal = old_base + "-wal"
        with open(old_wal, "wb") as f:
            f.write(b"fake-wal-bytes")
        _touch_mtime(old_wal, _day_ts(now, 0, 0))

        new_base = os.path.join(tree, "superboss-register.sqlite.20260806-fresh.bak")
        _make_valid_db(new_base)
        _touch_mtime(new_base, _day_ts(now, 0, 3600))

        report = m.run([tree], {"superboss-register.sqlite": live}, execute=True)

        assert not os.path.isfile(old_base)
        assert not os.path.isfile(old_wal), "the -wal sidecar must be deleted together with its main file"
        assert os.path.isfile(new_base)
        deleted_bases = {os.path.basename(p) for i in report["trees"][0]["items"]
                          if i["action"] == "deleted" for p in i["deleted_paths"]}
        assert deleted_bases == {os.path.basename(old_base), os.path.basename(old_wal)}


def test_live_db_and_its_own_companions_are_never_discovered_as_candidates():
    m = _load_module()
    with tempfile.TemporaryDirectory() as tree, tempfile.TemporaryDirectory() as mem:
        live = os.path.join(mem, "superboss-register.sqlite")
        _make_valid_db(live)
        # Defensive scenario: even if a live DB's own files sat inside a scanned tree
        # (not true for either real tree, but must never be a candidate if it happened).
        live_in_tree = os.path.join(tree, "superboss-register.sqlite")
        _make_valid_db(live_in_tree)
        for suffix in ("-wal", "-shm", ".writelock"):
            open(live_in_tree + suffix, "wb").close()

        groups = m.discover_groups_for_db(tree, "superboss-register.sqlite")
        assert groups == []


# ---------------------------------------------------------------------------
# CLI / subprocess-level tests
# ---------------------------------------------------------------------------

def test_cli_dry_run_default_is_no_execute_flag_and_zero_writes():
    now = time.time()
    with tempfile.TemporaryDirectory() as tree, tempfile.TemporaryDirectory() as mem:
        live = os.path.join(mem, "superboss-register.sqlite")
        _make_valid_db(live)
        old = os.path.join(tree, "superboss-register.sqlite.a.bak")
        new = os.path.join(tree, "superboss-register.sqlite.b.bak")
        _make_valid_db(old); _touch_mtime(old, _day_ts(now, 0, 0))
        _make_valid_db(new); _touch_mtime(new, _day_ts(now, 0, 3600))

        out = subprocess.run(
            [sys.executable, SCRIPT_PATH, "--tree", tree,
             "--db", f"superboss-register.sqlite={live}"],
            capture_output=True, text=True, timeout=60)
        assert out.returncode == 0
        assert os.path.isfile(old), "no --execute flag means real, unconditional dry-run -- nothing deleted"
        assert os.path.isfile(new)
        # JSON report is the last stdout block -- locate it by its opening brace.
        json_start = out.stdout.index("{")
        parsed = json.loads(out.stdout[json_start:])
        assert parsed["mode"] == "dry-run"


def test_cli_execute_flag_actually_deletes_and_exits_0_when_healthy():
    now = time.time()
    with tempfile.TemporaryDirectory() as tree, tempfile.TemporaryDirectory() as mem:
        live = os.path.join(mem, "superboss-register.sqlite")
        _make_valid_db(live)
        old = os.path.join(tree, "superboss-register.sqlite.a.bak")
        new = os.path.join(tree, "superboss-register.sqlite.b.bak")
        _make_valid_db(old); _touch_mtime(old, _day_ts(now, 0, 0))
        _make_valid_db(new); _touch_mtime(new, _day_ts(now, 0, 3600))

        out = subprocess.run(
            [sys.executable, SCRIPT_PATH, "--tree", tree,
             "--db", f"superboss-register.sqlite={live}", "--execute"],
            capture_output=True, text=True, timeout=60)
        assert out.returncode == 0
        assert not os.path.isfile(old)
        assert os.path.isfile(new)


def test_cli_execute_exits_1_when_r4_aborts():
    now = time.time()
    with tempfile.TemporaryDirectory() as tree, tempfile.TemporaryDirectory() as mem:
        live = os.path.join(mem, "superboss-register.sqlite")
        _make_corrupt_file(live)
        old = os.path.join(tree, "superboss-register.sqlite.a.bak")
        new = os.path.join(tree, "superboss-register.sqlite.b.bak")
        _make_valid_db(old); _touch_mtime(old, _day_ts(now, 0, 0))
        _make_valid_db(new); _touch_mtime(new, _day_ts(now, 0, 3600))

        out = subprocess.run(
            [sys.executable, SCRIPT_PATH, "--tree", tree,
             "--db", f"superboss-register.sqlite={live}", "--execute"],
            capture_output=True, text=True, timeout=60)
        assert out.returncode == 1
        assert os.path.isfile(old), "R4 abort via CLI must still leave real files untouched"


def test_cli_bad_db_argument_exits_2():
    out = subprocess.run(
        [sys.executable, SCRIPT_PATH, "--db", "not-a-valid-spec"],
        capture_output=True, text=True, timeout=60)
    assert out.returncode == 2


def test_default_trees_and_dbs_point_at_the_real_paths_named_in_the_report():
    """Real, documented default wiring -- both trees and both source DBs named in
    UMR-20260808-023802-1955's own report. Does not invoke run()/main(); just checks
    the module-level constants (no filesystem access against the real trees)."""
    m = _load_module()
    assert m.SQLITE_DAILY_DIR == "/opt/veridian/backups/sqlite-daily"
    assert m.MEMORY_BACKUPS_DIR == "/opt/veridian/ai-os/memory/backups"
    assert set(m.DEFAULT_TREES) == {m.SQLITE_DAILY_DIR, m.MEMORY_BACKUPS_DIR}
    assert set(m.DEFAULT_SOURCE_DBS) == {"superboss-register.sqlite", "credit-ledger.sqlite"}


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
