#!/usr/bin/env python3
import datetime, json, os, subprocess, sys, time
sys.path.insert(0, "/opt/veridian/scripts")
import dispatch_core  # noqa: E402

AI_OS = "/opt/veridian/ai-os"
TASKS_DIR = f"{AI_OS}/tasks"
GATEWAY = "/opt/veridian/scripts/task-gateway.py"
MAX_LOAD1 = 8 * 0.90


def wait_for_slot(label, timeout_s=150):
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


WAVES = [
    (5, "task-20260726-103756-adopted-adopt-recovered-lifecycle-fix-pr84-for-r", "claude-control",
     "Adopt recovered-lifecycle-fix PR84 for retroactive audit"),
    (6, "task-20260726-112208-adopted-write-gate-round-3--fix-spoofable-cgroup", "claude-control",
     "Write-gate round 3: fix spoofable cgroup file + force-push + multi-refspec (adopted)"),
    (7, "task-20260726-121633-adopted-write-gate-round-4--argv-position-fix", "claude-control",
     "Write-gate round 4: argv-position fix + task-registry cross-reference (adopted)"),
]

results = {"redispatched": [], "failed": []}
for wave_num, rep, repo, title in WAVES:
    prompt_path = f"{TASKS_DIR}/{rep}/prompt.txt"
    if not os.path.isfile(prompt_path):
        print(f"SKIP {rep}: no prompt.txt", file=sys.stderr)
        results["failed"].append(rep)
        continue
    if not wait_for_slot(rep):
        results["failed"].append(rep)
        continue
    prompt_text = open(prompt_path).read()
    submit = subprocess.run(
        ["python3", GATEWAY, "submit", "--text", prompt_text, "--source", "ai_agent",
         "--session-id", "finish-waves-5to8-2026-07-27"],
        capture_output=True, text=True,
    )
    try:
        instr_id = json.loads(submit.stdout).get("instruction_id")
    except Exception:
        instr_id = None
    if not instr_id:
        print(f"FAILED submit {rep}: {submit.stdout[-300:]} {submit.stderr[-200:]}", file=sys.stderr)
        results["failed"].append(rep)
        continue
    start = subprocess.run(
        ["python3", GATEWAY, "start", "--instruction-id", instr_id, "--title", title[:120],
         "--repo", repo, "--prompt-file", prompt_path],
        capture_output=True, text=True,
    )
    try:
        start_json = json.loads(start.stdout)
    except Exception:
        start_json = {"raw": start.stdout[-300:]}
    new_id = start_json.get("task_id")
    if new_id:
        results["redispatched"].append({"original": rep, "new_task_id": new_id, "wave": wave_num})
        dispatch_core.record_dispatch_event(
            new_id, dispatched_by="finish_waves_5to8.py",
            source_queue_or_plan="BACKLOG_COMPLETION_PLAN_2026-07-27_waves5-8",
            worker_unit=start_json.get("work_item_id"),
            extra={"action": "redispatch_of_original_prompt", "original_task_id": rep, "wave": wave_num},
        )
        print(f"OK wave {wave_num}: {rep} -> {new_id}")
    else:
        print(f"FAILED start {rep}: {start_json}", file=sys.stderr)
        results["failed"].append(rep)
    time.sleep(3)

print(json.dumps(results, indent=2))
