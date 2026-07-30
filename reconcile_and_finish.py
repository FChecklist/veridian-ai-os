#!/usr/bin/env python3
"""
reconcile_and_finish.py -- second pass over BACKLOG_COMPLETION_PLAN_2026-07-27.json.

Fixes a real bug found in round 1 (execute_backlog_plan.py): every task
routed to pending_review kept its OLD/default `branch` field (often the
repo's default branch, e.g. "master") instead of the real PR's branch, so
supervisor-entrypoint.sh failed every single one of the 8 round-1 supervisor
runs with "could not resolve a real PR for branch 'master'". This script:

  1. Corrects `branch` (and `repo` where that was also wrong) on every
     pending_review task using the REAL PR's headRefName via `gh pr view`,
     then re-triggers its supervisor -- one shot each, same as round 1.
  2. Collapses two real cross-issue duplicates round 1's dedup missed
     (different task slugs whose real committed work landed on the SAME
     PR): PR #562 (phase4-defense-in-depth-prompt-security /
     fix-pr562-defense-in-depth-integration-g) and PR #563
     (migration-drift-audit-and-reconciliation /
     resolve-pr563-conflict-properly). Only one representative per real PR
     gets routed; the other is marked superseded.
  3. Finishes the remaining redispatch waves (5-8) that round 1 didn't
     reach before it stalled.

Same resource guard and concurrency-cap reuse (dispatch_core.py) as round 1.
"""
import datetime
import json
import os
import subprocess
import sys
import time
import yaml

sys.path.insert(0, "/opt/veridian/scripts")
import dispatch_core  # noqa: E402

AI_OS = "/opt/veridian/ai-os"
TASKS_DIR = f"{AI_OS}/tasks"
PLAN_JSON = f"{AI_OS}/BACKLOG_COMPLETION_PLAN_2026-07-27.json"
GATEWAY = "/opt/veridian/scripts/task-gateway.py"
MAX_LOAD1 = 8 * 0.90


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def load(task_id):
    p = f"{TASKS_DIR}/{task_id}/task.yaml"
    with open(p) as f:
        return yaml.safe_load(f) or {}, p


def save(doc, path):
    with open(path, "w") as f:
        yaml.safe_dump(doc, f, default_flow_style=False, sort_keys=False)


def real_load1():
    return float(open("/proc/loadavg").read().split()[0])


def wait_for_slot(label, timeout_s=120):
    waited = 0
    while waited < timeout_s:
        with dispatch_core.acquire_dispatch_lock():
            if dispatch_core.has_free_slot() and real_load1() < MAX_LOAD1:
                return True
        time.sleep(5)
        waited += 5
    print(f"WARNING: no free slot for {label} after {timeout_s}s", file=sys.stderr)
    return False


def gh_pr_json(repo, pr_number, fields="headRefName,state,mergeable,url"):
    r = subprocess.run(["gh", "pr", "view", str(pr_number), "--repo", f"FChecklist/{repo}",
                         "--json", fields], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except Exception:
        return None


def pr_number_from_url(url):
    if not url:
        return None
    try:
        return int(url.rstrip("/").split("/")[-1])
    except ValueError:
        return None


def route_to_supervisor(task_id, repo, branch, results, extra_note=None):
    doc, path = load(task_id)
    review_json = f"{TASKS_DIR}/{task_id}/review.json"
    doc["status"] = "pending_review"
    doc["repo"] = repo
    doc["branch"] = branch
    doc["branch_corrected_at"] = now_iso()
    if extra_note:
        doc["branch_correction_note"] = extra_note
    save(doc, path)
    if os.path.exists(review_json):
        os.rename(review_json, review_json + f".pre-reroute2-{int(time.time())}.bak")

    if not wait_for_slot(task_id):
        results["deferred_no_slot"].append(task_id)
        return
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    r = subprocess.run(["systemctl", "--user", "start", f"veridian-supervisor@{task_id}.service"],
                        capture_output=True, text=True)
    if r.returncode == 0:
        results["reretried_supervisor"].append(task_id)
        dispatch_core.record_dispatch_event(
            task_id, dispatched_by="reconcile_and_finish.py",
            source_queue_or_plan="BACKLOG_COMPLETION_PLAN_2026-07-27_round2",
            worker_unit=f"veridian-supervisor@{task_id}.service",
            extra={"action": "branch_corrected_supervisor_retry", "branch": branch},
        )
        print(f"  re-started supervisor for {task_id} (branch={branch})")
    else:
        results["supervisor_start_failed"].append({"task_id": task_id, "stderr": r.stderr[:300]})
        print(f"  FAILED restart for {task_id}: {r.stderr[:200]}", file=sys.stderr)
    time.sleep(3)


def mark_superseded(task_id, dup_of, reason, results):
    doc, path = load(task_id)
    if doc.get("status") == "superseded":
        return
    doc["status"] = "superseded"
    doc["duplicate_of"] = dup_of
    doc["superseded_reason"] = reason
    doc["superseded_at"] = now_iso()
    save(doc, path)
    results["duplicates_marked"].append(task_id)


def main():
    with open(PLAN_JSON) as f:
        plan = json.load(f)
    by_rep = {i["representative_task_id"]: i for i in plan["issues"]}

    results = {
        "reretried_supervisor": [], "supervisor_start_failed": [], "duplicates_marked": [],
        "redispatched": [], "redispatch_submit_failed": [], "redispatch_start_failed": [],
        "deferred_no_slot": [], "started_at": now_iso(),
    }

    print("=== STEP 1: cross-issue duplicate reconciliation (PR #562, PR #563) ===")
    mark_superseded(
        "task-20260726-063532-fix-pr562-defense-in-depth-integration-g",
        "task-20260726-043023-phase4-defense-in-depth-prompt-security",
        "Real work landed on the same branch/PR #562 as phase4-defense-in-depth-prompt-security "
        "(round-1 dedup missed this cross-issue link -- neither task's own checkpoint text named "
        "the other's PR number). Confirmed via `gh pr view 562`: PR contains both the original "
        "phase-4 commit and the audit-fix commit from this task.",
        results,
    )
    mark_superseded(
        "task-20260726-071400-migration-drift-audit-and-reconciliation",
        "task-20260726-154338-resolve-pr563-conflict-properly--v2--exp",
        "Real work landed on the same branch/PR #563 as resolve-pr563-conflict-properly--v2--exp "
        "(round-1 dedup missed this cross-issue link). PR #563 is already routed to supervisor "
        "under that representative -- do not route this one separately.",
        results,
    )

    print("=== STEP 2: branch/repo correction + supervisor re-retry for round-1 failures ===")
    # (task_id, repo, pr_number_or_None, pr_url_field_task_id_or_None)
    fixups = [
        ("task-20260726-171226-tier2-fix--pr-80-round-5----close-git-gh", "claude-control", 98),
        ("task-20260726-172009-e-invoicing-per-line-gstrt-fix---irp-for", "compliance-tracker", None),
        ("task-20260726-172013-cityline-ticketing-6-role-reverse-engine", "infisuite-reverse-engineering", None),
        ("task-20260726-171420-phase5-browser-execution-lite-llm-npu-bu", "compliance-tracker", None),
        ("task-20260726-171950-preview-deployment-spot-check", "compliance-tracker", 571),
        ("task-20260726-154338-resolve-pr563-conflict-properly--v2--exp", "compliance-tracker", 563),
        ("task-20260726-194912-rca-task-20260726-171942-serverless-reso", "compliance-tracker", 581),
        ("task-20260726-194915-rca-task-20260726-171946-chat-context", "compliance-tracker", 580),
        ("task-20260726-194917-rca-task-20260726-172004-search-performa", "compliance-tracker", 582),
        ("task-20260726-194920-rca-task-20260726-172016-mother-router-a", "compliance-tracker", None),
        ("task-20260726-195243-rca-task-20260726-171954-storage-rls---b", "compliance-tracker", 575),
        ("task-20260726-195246-rca-task-20260726-172000-hr-performance", "compliance-tracker", None),
        ("task-20260726-043023-phase4-defense-in-depth-prompt-security", "compliance-tracker", 562),
    ]
    for task_id, repo, pr_number in fixups:
        doc, _ = load(task_id)
        if doc.get("status") == "superseded":
            print(f"  SKIP {task_id}: superseded")
            continue
        pr_num = pr_number
        if pr_num is None:
            url = doc.get("opened_pr_url")
            pr_num = pr_number_from_url(url)
        if pr_num is None:
            print(f"  SKIP {task_id}: no PR number resolvable", file=sys.stderr)
            continue
        pr = gh_pr_json(repo, pr_num)
        if not pr or not pr.get("headRefName"):
            print(f"  SKIP {task_id}: gh pr view {pr_num} failed", file=sys.stderr)
            continue
        route_to_supervisor(task_id, repo, pr["headRefName"], results,
                             extra_note=f"round-1 left branch=master (or wrong repo); corrected to "
                                        f"real PR #{pr_num} headRefName")

    print("=== STEP 3: finish remaining redispatch waves 5-8 ===")
    redispatch_cats = {"NEEDS_FRESH_REDISPATCH", "PR_CLOSED_NEEDS_REDISPATCH"}
    already_new_ids = set()
    # task_ids that ALREADY got a fresh redispatch in round 1 -- don't duplicate again
    round1_redispatched_originals = {
        "task-20260726-094625-re-verify-20-engine-inventory---confirm",
        "task-20260726-195236-rca-task-20260726-083946-fix-task-lifecy",
        "task-20260726-210059-integrate-knowledge-engine---wiring-regi",  # handled manually this session (PR #103)
        "task-20260726-101257-fix-owner-engine-integration--clarificat",
    }
    waves = {}
    for issue in plan["issues"]:
        if issue["classification"]["category"] in redispatch_cats and issue.get("wave"):
            if issue["representative_task_id"] in round1_redispatched_originals:
                continue
            if issue.get("wave", 0) < 5:
                continue  # waves 1-4 already handled in round 1 (or manually, for wave 2's item)
            waves.setdefault(issue["wave"], []).append(issue)

    for wave_num in sorted(waves):
        print(f"  -- wave {wave_num} --")
        for issue in waves[wave_num]:
            rep = issue["representative_task_id"]
            prompt_path = f"{TASKS_DIR}/{rep}/prompt.txt"
            if not os.path.isfile(prompt_path):
                print(f"  SKIP {rep}: no prompt.txt", file=sys.stderr)
                continue
            if not wait_for_slot(rep):
                results["deferred_no_slot"].append(rep)
                continue
            prompt_text = open(prompt_path).read()
            submit = subprocess.run(
                ["python3", GATEWAY, "submit", "--text", prompt_text,
                 "--source", "ai_agent", "--session-id", "reconcile-and-finish-2026-07-27"],
                capture_output=True, text=True,
            )
            try:
                instr_id = json.loads(submit.stdout).get("instruction_id")
            except Exception:
                instr_id = None
            if not instr_id:
                print(f"  FAILED submit {rep}: {submit.stdout[-300:]}", file=sys.stderr)
                results["redispatch_submit_failed"].append(rep)
                continue
            start = subprocess.run(
                ["python3", GATEWAY, "start", "--instruction-id", instr_id,
                 "--title", issue["title"][:120], "--repo", issue["repo"],
                 "--prompt-file", prompt_path],
                capture_output=True, text=True,
            )
            try:
                start_json = json.loads(start.stdout)
            except Exception:
                start_json = {"raw": start.stdout[-300:]}
            new_id = start_json.get("task_id")
            if new_id:
                results["redispatched"].append({"original": rep, "new_task_id": new_id})
                dispatch_core.record_dispatch_event(
                    new_id, dispatched_by="reconcile_and_finish.py",
                    source_queue_or_plan="BACKLOG_COMPLETION_PLAN_2026-07-27_round2",
                    worker_unit=start_json.get("work_item_id"),
                    extra={"action": "redispatch_of_original_prompt", "original_task_id": rep, "wave": wave_num},
                )
                print(f"  redispatched {rep} -> {new_id}")
            else:
                results["redispatch_start_failed"].append({"task_id": rep, "detail": start_json})
                print(f"  FAILED start {rep}: {start_json}", file=sys.stderr)
            time.sleep(3)

    results["finished_at"] = now_iso()
    out = f"{AI_OS}/RECONCILE_AND_FINISH_RESULT_2026-07-27.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n=== DONE: {out} ===")
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in results.items()}, indent=2))


if __name__ == "__main__":
    main()
