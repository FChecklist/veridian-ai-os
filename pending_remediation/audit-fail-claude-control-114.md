<!-- DRAFTED BY scripts/status-remediation-tick.py at 2026-07-30T05:58:15.416423+00:00 -->
<!-- classification: genuine_audit_fail (judgment_needed) -->
<!-- reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race. -->
<!-- STATUS: drafted, needs assistant review before dispatch (not auto-dispatched) -->

## OBJECTIVE
Fix the real AUDIT: FAIL finding on open PR https://github.com/FChecklist/claude-control/pull/114 (compliance-tracker/claude-control/projexa worker-review pipeline) so a re-review can pass, without touching unrelated code.

## SCOPE
Read the real AUDIT: FAIL comment body on https://github.com/FChecklist/claude-control/pull/114 in full (`gh api repos/FChecklist/claude-control/issues/114/comments`) and the real diff (`gh pr diff 114 --repo FChecklist/claude-control`). Address every issue it lists with a real code change on the existing PR branch `worker/task-20260726-181517-rca-task-20260726-171926-remove-anthropi`, not a new branch. Do not re-argue the finding -- if it is factually wrong, say so explicitly in the corrective commit message with evidence, do not silently ignore it.

## KNOWN_CONTEXT
Raised automatically by scripts/status-remediation-tick.py (classification: genuine_audit_fail, reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race.). Full finding excerpt:
AUDIT: FAIL
Objective Understood: Reviewed worker task 'rca-task-20260726-171926-remove-anthropic-api-key-dead-code-path' (risk tier: tier1) by reading the actual diff, not a self-report.
Standards Reviewed: AGENTS.md Operating Rule 7c structured audit protocol; risk-tier.py's deterministic tier classification.
Scope Confirmed:  scripts/veridian-task-watchdog.py          |  55 ++++++++++++++
 tests/veridian_task_watchdog_dedup_test.py | 118 +++++++++++++++++++++++++++++
 2 files changed, 173 insertions(+)
Evidence Recorded: The dedup code itself (rca_already_in_flight(), title-based glob scan over task.yaml, TERMINAL_TASK_STATUSES filter, plus regression tests) is competently written and correctly tested in isolation, but this branch is stale duplicate work that must not be merged: it forked scripts/veridian-task-watchdog.py from the pre-fix version (commit 3af111b, 2026-07-23) and independently reimplements the exact same step_3 RCA-dedup goal that master already solved via a different, more complete mechanism -- PR #110 'Add Server Resource Governor' (commit 4b151ce, merged into master 2026-07-27T07:09:05Z), which added task_identity-based dedup inside resource_governor.submit() 

## SUCCESS_CRITERIA
- `gh pr view 114 --repo FChecklist/claude-control --json state` still shows OPEN and mergeable after the fix
- A new commit exists on the branch after 2026-07-27T14:46:48Z that addresses each listed issue
- The next AUDIT comment on this PR is AUDIT: PASS, not AUDIT: FAIL

## EXPECTED_OUTPUT
A real corrective commit pushed to https://github.com/FChecklist/claude-control/pull/114's branch, and a checkpoint note summarizing which of the listed issues were fixed vs disputed (with evidence).

## CONSTRAINTS
Do not merge this PR yourself. Do not modify audit/review scripts to make the finding pass without a real code fix. Stay within the files the original PR touched plus whatever files the finding requires changing.

## COMPLEXITY_TIER
judgment
