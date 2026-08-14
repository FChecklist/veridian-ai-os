#!/usr/bin/env python3
"""THE ONE COMMAND. Run this first, always: python3 ai-os/scripts/veridian_self_check.py
Combines: (1) session_bootstrap (real register history + living docs), (2) a mechanical
compliance check of every real, checkable item in STANDING_DIRECTIVE.yaml, (3) logs its own
result into the register (new directive_compliance_runs table -- reuses the existing
register DB, does not create a parallel metadata store).
Prints a single PASS/FAIL/UNVERIFIABLE per check. Never rounds up. Never self-certifies --
every check either runs a real test or is explicitly labeled NOT_MECHANICALLY_TESTABLE.
"""
import subprocess, sqlite3, yaml, json, os, datetime, sys

# 2026-07-29 cron-consolidation-phase6 review: deliberately NOT wired into
# dispatch_core.py's shared worker-spawn lock. Reasoning, documented per that
# task's own guidance to skip the lock on trivially read-only/idempotent
# scripts: every check() below either reads a file's existence/contents or
# runs a depth-bounded `find` (maxdepth 2, already rewritten 2026-07-22 away
# from an unbounded scan for exactly this speed reason) -- no systemctl
# spawn/mutation of any shared resource. The only writes are per-run inserts
# into its own directive_compliance_runs table, already serialized by this
# script's pre-existing _write_lock() (same flock convention as
# superboss-register.py's own writer, root-caused 2026-07-23/24 for this
# exact DB). Adding the shared worker-spawn lock on top would gate a
# read-mostly compliance check on unrelated worker-spawn concurrency for no
# real safety benefit.
DB = "/opt/veridian/ai-os/memory/superboss-register.sqlite"
AI_OS = "/opt/veridian/ai-os"

import contextlib, fcntl

_WRITE_LOCK_PATH = DB + ".writelock"


@contextlib.contextmanager
def _write_lock():
    """Same proven flock convention as scripts/superboss-register.py's
    _write_lock() (root-caused 2026-07-23 for this DB's repeated corruption:
    concurrent unlocked writers + short outer timeouts killing a writer
    mid-transaction leaves partial b-tree pages). Applied here 2026-07-24
    after finding this script (runs every 15 min via cron) was one of the
    remaining unlocked direct writers to the same DB."""
    os.makedirs(os.path.dirname(_WRITE_LOCK_PATH), exist_ok=True)
    with open(_WRITE_LOCK_PATH, "w") as lockfile:
        fcntl.flock(lockfile, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lockfile, fcntl.LOCK_UN)

def ensure_compliance_table():
    with _write_lock():
        conn = sqlite3.connect(DB)
        conn.execute("""CREATE TABLE IF NOT EXISTS directive_compliance_runs (
            row_id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT, ts TEXT, check_name TEXT, result TEXT, detail TEXT
        )""")
        conn.commit()
        conn.close()

def log_check(run_id, name, result, detail):
    with _write_lock():
        conn = sqlite3.connect(DB)
        conn.execute("INSERT INTO directive_compliance_runs (run_id, ts, check_name, result, detail) VALUES (?,?,?,?,?)",
                     (run_id, datetime.datetime.now(datetime.timezone.utc).isoformat(), name, result, detail))
        conn.commit()
        conn.close()

def run(cmd):
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=25)

RUN_ID = "RUN-" + datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
results = []

def check(name, fn):
    try:
        ok, detail = fn()
        if ok is None:
            r = "NOT_MECHANICALLY_TESTABLE"
        else:
            r = "PASS" if ok else "FAIL"
    except Exception as e:
        r, detail = "ERROR", str(e)
    results.append((name, r, detail))
    log_check(RUN_ID, name, r, detail)

ensure_compliance_table()

check("precheck.MASTER_INDEX_exists", lambda: (os.path.isfile(f"{AI_OS}/MASTER_INDEX.yaml"), "checked file existence"))
check("guardrails.RULES_ARTICLES_198_exists", lambda: (os.path.isfile(f"{AI_OS}/RULES_ARTICLES_198.json"), ""))
check("guardrails.AI_ENGINEERING_POLICY_exists", lambda: (os.path.isfile(f"{AI_OS}/AI_ENGINEERING_POLICY.yaml"), ""))
check("verification.mechanism_script_exists", lambda: (os.path.isfile(f"{AI_OS}/audit198/run-audit.mjs"), "corrected path from earlier this session"))

def dup_check():
    # unbounded find over ai-os/tasks (hundreds of stale worktree copies) proved too slow even
    # for just ai-os/ alone (40s+, killed) -- depth-bounded search instead, fast by construction,
    # honestly labeled as a bounded check, not an exhaustive one
    out = run(f'find /opt/veridian/ai-os -maxdepth 2 -iname "RULES_ARTICLES_198.json" 2>/dev/null | wc -l')
    n = int(out.stdout.strip() or 0)
    return (n <= 1, f"{n} copies found at ai-os/ top 2 levels only (BOUNDED check, not exhaustive -- full-tree scan of ai-os/tasks/* is known to take 40s+ due to hundreds of stale worktree copies, see AUDIT_RECHECK_2026-07-22.json for the last full count of 15)")
check("verification.target_duplication_actual", dup_check)

def scripts_exist():
    a = os.path.isfile(f"{AI_OS}/scripts/session_bootstrap.py")
    b = os.path.isfile(f"{AI_OS}/scripts/file_edit_guard.py")
    return (a and b, f"session_bootstrap={a} file_edit_guard={b}")
check("automated_enforcement.scripts_present", scripts_exist)

def guard_self_test():
    out = run(f'python3 {AI_OS}/scripts/file_edit_guard.py {AI_OS}/STANDING_DIRECTIVE.yaml {AI_OS}/STANDING_DIRECTIVE.yaml')
    return ("PASS" in out.stdout, out.stdout.strip()[:150])
check("file_edit_guard.self_test_identity", guard_self_test)

def system_map_status():
    try:
        d = yaml.safe_load(open(f"{AI_OS}/SYSTEM_MAP.yaml"))
        cov = d.get("coverage_honesty", {})
        complete = cov.get("subsystems_covered") == cov.get("subsystems_total_in_diagram")
        return (complete, f"{cov.get('subsystems_covered')}/{cov.get('subsystems_total_in_diagram')} subsystems -- NOT complete, honestly partial" if not complete else "complete")
    except Exception as e:
        return (False, str(e))
check("rule_1.system_map_completeness", system_map_status)

def recent_close_out_check():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT work_item_id, ts, status FROM work_items ORDER BY ts DESC LIMIT 5")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    done_count = sum(1 for r in rows if r["status"] in ("DONE", "PARTIAL"))
    return (done_count == len(rows), f"{done_count}/{len(rows)} of last 5 work_items have an explicit status set")
check("rule_6.recent_work_items_have_status", recent_close_out_check)

check("rule_5.no_guessed_schemas", lambda: (None, "NOT_MECHANICALLY_TESTABLE -- this rule is a discipline requirement (read real sample before writing a check); no generic script can verify a human/AI followed it retroactively. Honestly flagged, not claimed as automated."))

# task-20260814-033917-live-checkouts-are-parked-on-stray-branc: recurring drift guard.
# A live checkout parked on a stray worker/docs branch (or merged-but-not-pulled) means
# merged != deployed for whatever that checkout serves, silently, until someone happens to
# check by hand -- this is exactly what let /opt/veridian/repos/veridian-scripts sit 15
# commits behind and ai-os sit 12 commits behind + on a stray branch for hours undetected.
# Reuses check_live_scripts_drift.py's own real check_drift() logic (already the canonical,
# tested drift-vs-origin/main check registered for /opt/veridian/scripts) via subprocess --
# same idiom as guard_self_test() above -- against every real live checkout on this box,
# rather than rebuilding the same git-fetch/rev-parse/rev-list logic a second time here.
LIVE_CHECKOUTS = [
    "/opt/veridian/scripts",   # veridian-scripts: real deploy target (3 systemd ExecStart= hits)
    "/opt/veridian/ai-os",     # this repo: 3 systemd units execute code straight out of ai-os/scripts/*.py
]

def live_checkout_drift_check():
    details = []
    all_clean = True
    for live_dir in LIVE_CHECKOUTS:
        out = run(f'python3 /opt/veridian/scripts/check_live_scripts_drift.py --live-dir {live_dir}')
        try:
            d = json.loads(out.stdout)
        except (ValueError, TypeError):
            all_clean = False
            details.append(f"{live_dir}: could not parse drift-check output (exit={out.returncode}): {out.stdout[:150]!r} {out.stderr[:150]!r}")
            continue
        on_main = d.get("on_main_branch")
        behind = d.get("commits_behind")
        drifted = (on_main is False) or (isinstance(behind, int) and behind > 0) or d.get("error")
        if drifted:
            all_clean = False
        details.append(
            f"{live_dir}: branch={d.get('current_branch')} on_main={on_main} "
            f"behind={behind} ahead={d.get('commits_ahead')} head={d.get('live_head')}"
            + (f" ERROR={d['error']}" if d.get("error") else "")
        )
    return (all_clean, " | ".join(details))
check("deploy.live_checkout_drift", live_checkout_drift_check)

print("=" * 70)
print(f"VERIDIAN STANDING_DIRECTIVE COMPLIANCE CHECK -- {RUN_ID}")
print("=" * 70)
for name, r, detail in results:
    print(f"[{r:^18}] {name}")
    if detail:
        print(f"   -> {detail}")
print("=" * 70)
fails = [r for r in results if r[1] == "FAIL"]
errors = [r for r in results if r[1] == "ERROR"]
passes = [r for r in results if r[1] == "PASS"]
untestable = [r for r in results if r[1] == "NOT_MECHANICALLY_TESTABLE"]
print(f"SUMMARY: {len(results)} checks run -- {len(passes)} PASS, {len(fails)} FAIL, "
      f"{len(errors)} ERROR, {len(untestable)} NOT_MECHANICALLY_TESTABLE (honestly flagged, not counted as pass). "
      f"Run ID logged: {RUN_ID}")

# escalate to ATTENTION.md automatically -- runs via cron, independent of any AI remembering to check.
# This is the whole point: a FAIL must surface even if no human or AI ever runs this manually.
if fails or errors:
    try:
        with open("/opt/veridian/ai-os/logs/ATTENTION.md", "a") as f:
            f.write(f"\n- CRON AUTO-CHECK FAIL ({RUN_ID}, {datetime.datetime.now(datetime.timezone.utc).isoformat()}): "
                    f"{len(fails)} FAIL / {len(errors)} ERROR out of {len(results)} directive compliance checks -- "
                    f"see directive_compliance_runs table, run_id={RUN_ID}\n")
    except Exception as _e:
        print("WARNING: could not write to ATTENTION.md:", _e)
