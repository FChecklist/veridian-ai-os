#!/usr/bin/env python3
"""round 3: apply the confirmed-real branch fixes to the 6 items that hit a
transient `gh pr view` failure in round 2, plus preview-deployment (now
correctly pointed at real PR #573), plus check on remaining wave 5-8
redispatch status."""
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


def wait_for_slot(label, timeout_s=120):
    waited = 0
    while waited < timeout_s:
        with dispatch_core.acquire_dispatch_lock():
            load1 = float(open("/proc/loadavg").read().split()[0])
            if dispatch_core.has_free_slot() and load1 < MAX_LOAD1:
                return True
        time.sleep(5)
        waited += 5
    print(f"WARNING: no slot for {label}", file=sys.stderr)
    return False


fixups = [
    ("task-20260726-194912-rca-task-20260726-171942-serverless-reso", "compliance-tracker",
     "worker/task-20260726-171942-serverless-resource-limit-tradeoff-doc"),
    ("task-20260726-194915-rca-task-20260726-171946-chat-context", "compliance-tracker",
     "worker/task-20260726-171946-chat-context---terminology---mode-pill-a"),
    ("task-20260726-194917-rca-task-20260726-172004-search-performa", "compliance-tracker",
     "worker/task-20260726-172004-search-performance-explain-analyze---gin"),
    ("task-20260726-194920-rca-task-20260726-172016-mother-router-a", "compliance-tracker",
     "feat/mother-router-roster-persistent-memory"),
    ("task-20260726-195243-rca-task-20260726-171954-storage-rls---b", "compliance-tracker",
     "worker/task-20260726-171954-storage-rls---backup-pitr---supabase-mon"),
    ("task-20260726-195246-rca-task-20260726-172000-hr-performance", "compliance-tracker",
     "worker/task-20260726-172000-hr-performance-error-handling---payroll"),
    ("task-20260726-171950-preview-deployment-spot-check", "compliance-tracker",
     "worker/task-20260726-171950-preview-deployment-spot-check"),
]

results = {"reretried": [], "failed": []}
for task_id, repo, branch in fixups:
    doc, path = load(task_id)
    if doc.get("status") == "superseded":
        print(f"SKIP {task_id}: superseded")
        continue
    review_json = f"{TASKS_DIR}/{task_id}/review.json"
    doc["status"] = "pending_review"
    doc["repo"] = repo
    doc["branch"] = branch
    doc["branch_corrected_at"] = now_iso()
    save(doc, path)
    if os.path.exists(review_json):
        os.rename(review_json, review_json + f".pre-reroute3-{int(time.time())}.bak")

    if not wait_for_slot(task_id):
        results["failed"].append(task_id)
        continue
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    r = subprocess.run(["systemctl", "--user", "start", f"veridian-supervisor@{task_id}.service"],
                        capture_output=True, text=True)
    if r.returncode == 0:
        results["reretried"].append(task_id)
        dispatch_core.record_dispatch_event(
            task_id, dispatched_by="reconcile_round3.py",
            source_queue_or_plan="BACKLOG_COMPLETION_PLAN_2026-07-27_round3",
            worker_unit=f"veridian-supervisor@{task_id}.service",
            extra={"action": "branch_corrected_supervisor_retry_round3", "branch": branch},
        )
        print(f"OK {task_id} (branch={branch})")
    else:
        results["failed"].append(task_id)
        print(f"FAILED {task_id}: {r.stderr[:200]}", file=sys.stderr)
    time.sleep(3)

with open(f"{AI_OS}/RECONCILE_ROUND3_RESULT_2026-07-27.json", "w") as f:
    json.dump(results, f, indent=2)
print(json.dumps(results, indent=2))
