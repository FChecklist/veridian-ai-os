<!-- DRAFTED BY scripts/veridian_remediation_dispatcher.py at 2026-07-26T09:50:54.576564+00:00 -->
<!-- classification: genuine_audit_fail (judgment_needed) -->
<!-- reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race. -->
<!-- STATUS: drafted, needs assistant review before dispatch (not auto-dispatched) -->

## OBJECTIVE
Fix the real AUDIT: FAIL finding on open PR https://github.com/FChecklist/claude-control/pull/81 (compliance-tracker/claude-control/projexa worker-review pipeline) so a re-review can pass, without touching unrelated code.

## SCOPE
Read the real AUDIT: FAIL comment body on https://github.com/FChecklist/claude-control/pull/81 in full (`gh api repos/FChecklist/claude-control/issues/81/comments`) and the real diff (`gh pr diff 81 --repo FChecklist/claude-control`). Address every issue it lists with a real code change on the existing PR branch `worker/task-20260726-091933-fix-task-lifecycle--real-branch-resoluti`, not a new branch. Do not re-argue the finding -- if it is factually wrong, say so explicitly in the corrective commit message with evidence, do not silently ignore it.

## KNOWN_CONTEXT
Raised automatically by scripts/veridian_remediation_dispatcher.py (classification: genuine_audit_fail, reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race.). Full finding excerpt:
AUDIT: FAIL
Objective Understood: Reviewed worker task 'Fix TASK lifecycle: real branch resolution + real HOLD_FOR_OWNER_SIGNOFF (redispatch after API limit)' (risk tier: tier1) by reading the actual diff, not a self-report.
Standards Reviewed: AGENTS.md Operating Rule 7c structured audit protocol; risk-tier.py's deterministic tier classification.
Scope Confirmed:  ai-os/OWNER_DIRECTIVES/PROTOCOL_OWNER_AI.yaml |  33 ++
 scripts/supervisor-entrypoint.sh              | 371 ++++++++++++++++++
 scripts/task-gateway.py                       |  13 +-
 scripts/tight_task_validation.py              |  33 +-
 scripts/veridian-task.py                      | 523 ++++++++++++++++++++++++++
 tests/hold_for_signoff_test.py                | 161 ++++++++
 tests/veridian_task_branch_resolution_test.py | 167 ++++++++
 7 files changed, 1298 insertions(+), 3 deletions(-)
Evidence Recorded: This diff is fully duplicate, already-merged work: every touched file (ai-os/OWNER_DIRECTIVES/PROTOCOL_OWNER_AI.yaml's A15 article, scripts/supervisor-entrypoint.sh, scripts/task-gateway.py, scripts/tight_task_validation.py, scripts/veridian-task.py, and both new test files) is byte-identical to what already exists 

## SUCCESS_CRITERIA
- `gh pr view 81 --repo FChecklist/claude-control --json state` still shows OPEN and mergeable after the fix
- A new commit exists on the branch after 2026-07-26T09:36:07Z that addresses each listed issue
- The next AUDIT comment on this PR is AUDIT: PASS, not AUDIT: FAIL

## EXPECTED_OUTPUT
A real corrective commit pushed to https://github.com/FChecklist/claude-control/pull/81's branch, and a checkpoint note summarizing which of the listed issues were fixed vs disputed (with evidence).

## CONSTRAINTS
Do not merge this PR yourself. Do not modify audit/review scripts to make the finding pass without a real code fix. Stay within the files the original PR touched plus whatever files the finding requires changing.

## COMPLEXITY_TIER
judgment
