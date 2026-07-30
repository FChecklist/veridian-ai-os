<!-- DRAFTED BY scripts/status-remediation-tick.py at 2026-07-30T05:58:15.419179+00:00 -->
<!-- classification: genuine_audit_fail (judgment_needed) -->
<!-- reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race. -->
<!-- STATUS: drafted, needs assistant review before dispatch (not auto-dispatched) -->

## OBJECTIVE
Fix the real AUDIT: FAIL finding on open PR https://github.com/FChecklist/compliance-tracker/pull/582 (compliance-tracker/claude-control/projexa worker-review pipeline) so a re-review can pass, without touching unrelated code.

## SCOPE
Read the real AUDIT: FAIL comment body on https://github.com/FChecklist/compliance-tracker/pull/582 in full (`gh api repos/FChecklist/compliance-tracker/issues/582/comments`) and the real diff (`gh pr diff 582 --repo FChecklist/compliance-tracker`). Address every issue it lists with a real code change on the existing PR branch `worker/task-20260726-172004-search-performance-explain-analyze---gin`, not a new branch. Do not re-argue the finding -- if it is factually wrong, say so explicitly in the corrective commit message with evidence, do not silently ignore it.

## KNOWN_CONTEXT
Raised automatically by scripts/status-remediation-tick.py (classification: genuine_audit_fail, reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race.). Full finding excerpt:
AUDIT: FAIL
Objective Understood: Reviewed worker task 'rca-task-20260726-172004-search-performance-explain-analyze---gin' (risk tier: tier1) by reading the actual diff, not a self-report.
Standards Reviewed: AGENTS.md Operating Rule 7c structured audit protocol; risk-tier.py's deterministic tier classification.
Scope Confirmed: 
Evidence Recorded: This task produced no real changes: the worker branch has zero commits beyond master's current tip (git log master..HEAD is empty and HEAD is a strict ancestor of master), the working tree is clean, and PROGRESS.md explicitly states the task is 'Not started'. There is no diff touching search performance, EXPLAIN ANALYZE output, or GIN indexing to review at all, so there is nothing here that meets tier1 bar for autonomous merge; this is claim-only/stub work with no underlying implementation. Issues found: No commits exist on this branch beyond master's tip; the task made zero code changes despite being marked for review.; PROGRESS.md still shows 'Not started' with no completed items, contradicting any expectation that this task reached a mergeable state.; No GIN index, migration, or query-plan (EXPLAIN ANALYZE) artifact is present anywher

## SUCCESS_CRITERIA
- `gh pr view 582 --repo FChecklist/compliance-tracker --json state` still shows OPEN and mergeable after the fix
- A new commit exists on the branch after 2026-07-27T04:19:55Z that addresses each listed issue
- The next AUDIT comment on this PR is AUDIT: PASS, not AUDIT: FAIL

## EXPECTED_OUTPUT
A real corrective commit pushed to https://github.com/FChecklist/compliance-tracker/pull/582's branch, and a checkpoint note summarizing which of the listed issues were fixed vs disputed (with evidence).

## CONSTRAINTS
Do not merge this PR yourself. Do not modify audit/review scripts to make the finding pass without a real code fix. Stay within the files the original PR touched plus whatever files the finding requires changing.

## COMPLEXITY_TIER
judgment
