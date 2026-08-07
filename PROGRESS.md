# PROGRESS -- task-20260807-052027-platform-integrity--worker-units-exit-0

## Completed
- [x] STEP 1: root cause confirmed with file+line evidence (see ROOT_CAUSE below)
- [x] STEP 2: fix implemented + pushed (ExecStopPost + worker-exit-status-bridge.py)
- [x] STEP 3: reconciler script implemented (reconcile_stale_running_workers.py)
- [x] STEP 4: reconciler run for real against the live DB, counts recorded below
- [x] veridian-scripts PR opened: https://github.com/FChecklist/veridian-scripts/pull/249

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

## Fix (STEP 2) -- DONE
Repo: veridian-scripts (NOT this task's own repo, veridian-ai-os -- worker-entrypoint.sh /
veridian-worker@.service / superboss-register.py all live there). Worktree:
/opt/veridian/repos/veridian-scripts-worker-exit0-wt, branch
worker/task-20260807-052027-platform-integrity--worker-units-exit-0, commit ce64927,
PR: https://github.com/FChecklist/veridian-scripts/pull/249 (open, awaiting merge --
worker-entrypoint.sh's own convention is "pushes the branch on success, never
merges/deploys", followed here too).
- Added `ExecStopPost=/opt/veridian/scripts/worker-exit-status-bridge.py %i` to
  systemd/veridian-worker@.service -- ExecStopPost runs on every stop (clean exit, non-zero
  exit, TimeoutStopSec, SIGKILL/OOM) per systemd semantics, unlike the bash `trap ... EXIT`
  already in worker-entrypoint.sh which cannot survive SIGKILL. Verified with
  `systemd-analyze --user verify` (exit 0, unit syntactically valid).
- New worker-exit-status-bridge.py: reads task.yaml's own last checkpoint status
  (the real, already-written signal) and only ever writes umr_tasks status=failed via
  `superboss-register.py mark-umr-terminal` for a definitively negative, no-more-automatic-
  progress outcome (task.yaml status in {failed, blocked, cancelled, rejected_duplicate,
  superseded, not_needed}). Never writes completed/completed_unmerged from this hook (no
  exit-code-based completion, ever) and never touches a row while task.yaml status is
  pending_review (supervisor handoff, genuinely still running) or in_progress/pending
  (ambiguous crash/kill mid-work -- left for the STEP 3 reconciler, since a hasty write here
  could race systemd's own Restart=on-failure retry and violate duplicate-safety). Always
  exits 0 itself (a non-zero ExecStopPost exit would corrupt the unit's own Result).

## Reconciler (STEP 3) -- DONE
reconcile_stale_running_workers.py in the same worktree/PR. Deterministic, idempotent,
re-runnable (`--execute` required for real writes, dry-run by default). Scope: umr_tasks rows
with status='running' AND unit_name LIKE 'veridian-worker@%' AND the live unit's ActiveState
!= active/activating/deactivating (via `systemctl --user show`). For each: resolves the real
task directory (outputs_json.new_task_id first, falling back to task_identity, falling back
to a reconcile-umr-<id> directory match), reads task.yaml, and decides using only real
artifacts -- via mark-umr-terminal/reset-umr-to-queued, never raw SQL:
- real completion_evidence (Rule 7), or a real branch-tip commit (git ls-remote, gated on the
  task ever having a non-empty files_modified at some checkpoint -- a real, live false-positive
  was found and closed here: task-20260718-164005-cloud-deployment--deployment-automation had
  a real UNCOMMITTED files_modified list yet its branch's own git-log tip was simply whatever
  origin/main already was -- zero real commits of its own), or the last checkpoint's own
  git-log-captured commit (only when that checkpoint's status was completed/pending_review AND
  its tree was clean -- covers a branch already deleted post-merge) -> attempt
  `mark-umr-terminal --status completed`, falling back to `--status completed_unmerged` on that
  specific refusal. Both gated by validate_umr_terminal_completion_evidence()'s own real,
  independent git-ancestry/file-exists check -- this script only ever supplies a candidate,
  never asserts the outcome.
- no accepted completion candidate, task.yaml's own last status in
  {failed, blocked, cancelled, rejected_duplicate, superseded, not_needed} -> `--status failed`.
- anything else (in_progress/pending with no accepted evidence) -> `reset-umr-to-queued`
  (duplicate-safe: reuses the SAME row, 'queued' is itself an active status so
  find_active_umr_by_identity's existing dedup check still sees it -- never inserts a new row).
Never flips a row to completed/completed_unmerged on process exit code alone.

## Real per-row disposition (STEP 4) -- DONE, real run against the live DB
Ran `reconcile_stale_running_workers.py --execute` once for real. 24 rows examined (live,
growing pool -- more workers settled mid-investigation):
- **completed: 3** (UMR-20260807-020846-772f, UMR-20260807-033052-f756, UMR-20260807-042701-a4c5
  -- all via a real, checkpoint-captured, clean-tree commit, each independently verified by
  mark-umr-terminal's own git-ancestry check)
- **completed_unmerged: 17** (real, currently-pushed branch tips, verified real+not-yet-merged
  by the same server-side gate)
- **requeued: 1** (UMR-20260806-223459-ce66 / task-20260718-164005-cloud-deployment--
  deployment-automation -- genuinely ambiguous: real uncommitted files_modified but zero real
  committed evidence anywhere; reset to queued via the same row, duplicate-safe)
- **skipped (genuinely still active/transitional): 3** (this task's own unit
  UMR-20260807-020911-7f31, plus 2 other units mid-run/mid-transition at execution time)
Full per-row JSON: RECONCILE_STALE_RUNNING_WORKERS_RESULT_2026-08-07.json (this directory).
Related task UMR-20260806-180933-d3bb (cited in this task's own SPEC) was found already
reconciled to status='failed' by a pre-existing Stage-1 heartbeat backfill
(resource_governor.py's backfill_null_heartbeats(), ran ~35 min before this task started) --
confirmed via its own umr_tasks.reason field, not re-touched here.

## Remaining
- [ ] none -- PR #249 awaits merge (out of scope for this task per worker-entrypoint.sh's own
      "push, never merge/deploy" convention)
