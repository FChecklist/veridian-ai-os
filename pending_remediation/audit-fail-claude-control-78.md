<!-- DRAFTED BY scripts/veridian_remediation_dispatcher.py at 2026-07-26T07:40:50.501094+00:00 -->
<!-- classification: genuine_audit_fail (judgment_needed) -->
<!-- reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race. -->
<!-- STATUS: drafted, needs assistant review before dispatch (not auto-dispatched) -->

## OBJECTIVE
Fix the real AUDIT: FAIL finding on open PR https://github.com/FChecklist/claude-control/pull/78 (compliance-tracker/claude-control/projexa worker-review pipeline) so a re-review can pass, without touching unrelated code.

## SCOPE
Read the real AUDIT: FAIL comment body on https://github.com/FChecklist/claude-control/pull/78 in full (`gh api repos/FChecklist/claude-control/issues/78/comments`) and the real diff (`gh pr diff 78 --repo FChecklist/claude-control`). Address every issue it lists with a real code change on the existing PR branch `worker/task-20260726-071221-close-worker-false-self-report-gap-in-ph`, not a new branch. Do not re-argue the finding -- if it is factually wrong, say so explicitly in the corrective commit message with evidence, do not silently ignore it.

## KNOWN_CONTEXT
Raised automatically by scripts/veridian_remediation_dispatcher.py (classification: genuine_audit_fail, reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race.). Full finding excerpt:
AUDIT: FAIL
Objective Understood: Reviewed worker task 'Close worker false-self-report gap in phase-plan YAML (real CI gate)' (risk tier: tier1) by reading the actual diff, not a self-report.
Standards Reviewed: AGENTS.md Operating Rule 7c structured audit protocol; risk-tier.py's deterministic tier classification.
Scope Confirmed:  ai-os/OWNER_DIRECTIVES/MEMORY_OWNER_AI.yaml |  32 +++
 scripts/backfill_phase_self_report.py       | 307 +++++++++++++++++++++++++++-
 tests/backfill_phase_self_report_test.py    | 141 +++++++++++++
 3 files changed, 470 insertions(+), 10 deletions(-)
Evidence Recorded: This diff adds a real, well-intentioned fix for the phase_4/PR#562 false-self-report incident: --audit-plans independently re-verifies every already-'done' phase against a real gh-confirmed merged PR and reverts (with a logged, committed incident) any that fail re-verification, and it is backed by a regression test that faithfully reproduces the real incident and passes. It correctly avoids the forbidden .github/workflows/** path, touches no auth/schema/migration/payment paths, and tier1 classification is appropriate for its blast radius on paper. However, confirm_merge() -- reused uncha

## SUCCESS_CRITERIA
- `gh pr view 78 --repo FChecklist/claude-control --json state` still shows OPEN and mergeable after the fix
- A new commit exists on the branch after 2026-07-26T07:26:57Z that addresses each listed issue
- The next AUDIT comment on this PR is AUDIT: PASS, not AUDIT: FAIL

## EXPECTED_OUTPUT
A real corrective commit pushed to https://github.com/FChecklist/claude-control/pull/78's branch, and a checkpoint note summarizing which of the listed issues were fixed vs disputed (with evidence).

## CONSTRAINTS
Do not merge this PR yourself. Do not modify audit/review scripts to make the finding pass without a real code fix. Stay within the files the original PR touched plus whatever files the finding requires changing.

## COMPLEXITY_TIER
judgment
