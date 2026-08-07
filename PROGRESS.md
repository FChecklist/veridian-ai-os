# PROGRESS -- task-20260807-052027-platform-integrity--worker-units-exit-0

## Completed
- [x] STEP 1: root cause confirmed with file+line evidence (see ROOT_CAUSE below)

## In progress
- [ ] STEP 2: fix (ExecStopPost on veridian-worker@.service + worker-exit-status-bridge.py)
- [ ] STEP 3: reconciler script
- [ ] STEP 4: run reconciler for real, record counts

## Root cause (STEP 1)
File: /opt/veridian/scripts/systemd/veridian-worker@.service (deployed copy:
/home/rajat/.config/systemd/user/veridian-worker@.service) -- the [Service] block has
ExecStart= only. There is NO ExecStopPost= directive anywhere in the unit (grep for
"ExecStopPost" over both the repo copy and the live deployed copy returns zero matches).

File: /opt/veridian/scripts/worker-entrypoint.sh -- every one of its ~13 exit points
(lines 47, 119, 126, 132, 373, 410, 517, 524, 584, 645, 661, 675, 680) calls
`python3 veridian-task.py checkpoint --status ...`, never
`superboss-register.py mark-umr-terminal`. veridian-task.py's cmd_checkpoint (line 695)
writes task.yaml + CONTROLLER.yaml (sync_controller_entry) and fires an audit-log call
(_auto_log_task_event -> `superboss-register.py log-action`, line 138) -- a log row, not
a status UPDATE. Nothing in cmd_checkpoint touches the umr_tasks table. grep for
"mark-umr-terminal"/"mark_umr_terminal"/"ExecStopPost" over worker-entrypoint.sh: zero
matches.

Real fact: umr_tasks.status is set to 'running' once, at dispatch time (resource_governor.py's
dispatch_one()), and is never written again by anything in the worker's own lifecycle. Every
"give up, no more retries" path in worker-entrypoint.sh (budget cap, preflight hard stop,
quality-gate exhausted, no-op pending_review handoff, quality-gates-passed handoff) disables
the unit and exits 0 -- ExecMainStatus=0, Result=success, systemd never restarts it -- while
umr_tasks silently keeps saying 'running' forever. That is the exact, confirmed shape of the
affected-row defect: two disconnected status-tracking systems (task.yaml/CONTROLLER.yaml vs.
umr_tasks), and only the first one is written on worker exit.

## Fix plan (STEP 2)
Repo: veridian-scripts (NOT this task's own repo, veridian-ai-os -- worker-entrypoint.sh /
veridian-worker@.service / superboss-register.py all live there). Worktree:
/opt/veridian/repos/veridian-scripts-worker-exit0-wt, branch
worker/task-20260807-052027-platform-integrity--worker-units-exit-0.
- Add `ExecStopPost=/opt/veridian/scripts/worker-exit-status-bridge.py %i` to
  systemd/veridian-worker@.service -- ExecStopPost runs on every stop (clean exit, non-zero
  exit, TimeoutStopSec, SIGKILL/OOM) per systemd semantics, unlike the bash `trap ... EXIT`
  already in worker-entrypoint.sh which cannot survive SIGKILL.
- New scripts/worker-exit-status-bridge.py: reads task.yaml's own last checkpoint status
  (the real, already-written signal) and only ever writes umr_tasks status=failed via
  `superboss-register.py mark-umr-terminal` for a definitively negative, no-more-automatic-
  progress outcome (task.yaml status in {failed, blocked, cancelled, rejected_duplicate}).
  Never writes completed/completed_unmerged from this hook (no exit-code-based completion,
  ever) and never touches a row while task.yaml status is pending_review (supervisor handoff,
  genuinely still running) or in_progress/pending (ambiguous crash/kill mid-work -- left for
  the STEP 3 reconciler, since a hasty write here could race systemd's own Restart=on-failure
  retry and violate duplicate-safety).

## Reconciler plan (STEP 3)
scripts/reconcile_stale_running_workers.py in the same worktree. Deterministic, idempotent,
re-runnable. Scope: umr_tasks rows with status='running' AND unit_name LIKE 'veridian-worker@%'
AND the live unit's ActiveState != active (via `systemctl --user show`). For each: resolves
the real task directory from outputs_json.new_task_id (falls back to task_identity match under
TASKS_DIR), reads task.yaml, and decides using only real artifacts:
- real branch commit that IS an ancestor of origin/main -> mark-umr-terminal --status completed
  (commit-sha, verified server-side by validate_umr_terminal_completion_evidence -- never our
  own guess)
- real branch commit that exists but is NOT yet an ancestor -> --status completed_unmerged
- task.yaml status in {failed, blocked, cancelled, rejected_duplicate} with no real unmerged
  commit evidence -> --status failed
- no task dir / no task.yaml / ambiguous (in_progress or pending with no commit evidence) ->
  `reset-umr-to-queued` (duplicate-safe: reuses find_active_umr_by_identity's existing
  UMR_ACTIVE_STATUSES check since 'queued' is itself an active status on the SAME row --
  never inserts a new umr_tasks row)
Never flips a row to completed/completed_unmerged on process exit code alone -- only on
`validate_umr_terminal_completion_evidence()`'s own real git-ancestry/file-exists check.

## Real per-row disposition (STEP 4)
Pending real run -- will be filled in with exact counts once executed.

## Remaining
- [ ] STEP 2 implementation
- [ ] STEP 3 implementation
- [ ] STEP 4 real run + report
