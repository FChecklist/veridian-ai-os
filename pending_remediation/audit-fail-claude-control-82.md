<!-- DRAFTED BY scripts/veridian_remediation_dispatcher.py at 2026-07-26T10:20:54.200443+00:00 -->
<!-- classification: genuine_audit_fail (judgment_needed) -->
<!-- reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race. -->
<!-- STATUS: drafted, needs assistant review before dispatch (not auto-dispatched) -->

## OBJECTIVE
Fix the real AUDIT: FAIL finding on open PR https://github.com/FChecklist/claude-control/pull/82 (compliance-tracker/claude-control/projexa worker-review pipeline) so a re-review can pass, without touching unrelated code.

## SCOPE
Read the real AUDIT: FAIL comment body on https://github.com/FChecklist/claude-control/pull/82 in full (`gh api repos/FChecklist/claude-control/issues/82/comments`) and the real diff (`gh pr diff 82 --repo FChecklist/claude-control`). Address every issue it lists with a real code change on the existing PR branch `worker/task-20260726-092433-wire-owner-engine---task-lifecycle-into`, not a new branch. Do not re-argue the finding -- if it is factually wrong, say so explicitly in the corrective commit message with evidence, do not silently ignore it.

## KNOWN_CONTEXT
Raised automatically by scripts/veridian_remediation_dispatcher.py (classification: genuine_audit_fail, reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race.). Full finding excerpt:
AUDIT: FAIL
Objective Understood: Reviewed worker task 'Wire OWNER_ENGINE + TASK lifecycle into one integrated engine (Owner priority)' (risk tier: tier1) by reading the actual diff, not a self-report.
Standards Reviewed: AGENTS.md Operating Rule 7c structured audit protocol; risk-tier.py's deterministic tier classification.
Scope Confirmed:  ai-os/OWNER_DIRECTIVES/PROTOCOL_OWNER_AI.yaml |  69 ++++++-
 scripts/prompt_gateway/engine/classifier.py   |  10 +
 scripts/prompt_gateway/gateway.py             | 251 +++++++++++++++++++++++++-
 scripts/task-gateway.py                       |  49 ++++-
 scripts/tight_task_validation.py              |  12 +-
 scripts/workflow_contract.py                  |  21 +++
 tests/test_gateway_task_integration.py        | 144 +++++++++++++++
 7 files changed, 535 insertions(+), 21 deletions(-)
Evidence Recorded: The core OWNER_ENGINE-to-TASK_GATEWAY wiring (gateway.py's new --mode owner-dispatch / route_and_dispatch / dispatch_to_task_lifecycle, the shared REQUIRED_TASK_SECTIONS dedup, and the classifier TASK_ID entity) is clean, additive, uses subprocess argv lists (no shell injection), and is genuinely covered by passing tests (verified: 5/5 pass loca

## SUCCESS_CRITERIA
- `gh pr view 82 --repo FChecklist/claude-control --json state` still shows OPEN and mergeable after the fix
- A new commit exists on the branch after 2026-07-26T09:46:09Z that addresses each listed issue
- The next AUDIT comment on this PR is AUDIT: PASS, not AUDIT: FAIL

## EXPECTED_OUTPUT
A real corrective commit pushed to https://github.com/FChecklist/claude-control/pull/82's branch, and a checkpoint note summarizing which of the listed issues were fixed vs disputed (with evidence).

## CONSTRAINTS
Do not merge this PR yourself. Do not modify audit/review scripts to make the finding pass without a real code fix. Stay within the files the original PR touched plus whatever files the finding requires changing.

## COMPLEXITY_TIER
judgment
