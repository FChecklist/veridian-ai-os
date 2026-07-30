<!-- DRAFTED BY scripts/status-remediation-tick.py at 2026-07-30T05:58:15.418733+00:00 -->
<!-- classification: genuine_audit_fail (judgment_needed) -->
<!-- reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race. -->
<!-- STATUS: drafted, needs assistant review before dispatch (not auto-dispatched) -->

## OBJECTIVE
Fix the real AUDIT: FAIL finding on open PR https://github.com/FChecklist/compliance-tracker/pull/585 (compliance-tracker/claude-control/projexa worker-review pipeline) so a re-review can pass, without touching unrelated code.

## SCOPE
Read the real AUDIT: FAIL comment body on https://github.com/FChecklist/compliance-tracker/pull/585 in full (`gh api repos/FChecklist/compliance-tracker/issues/585/comments`) and the real diff (`gh pr diff 585 --repo FChecklist/compliance-tracker`). Address every issue it lists with a real code change on the existing PR branch `feat/mother-router-roster-persistent-memory`, not a new branch. Do not re-argue the finding -- if it is factually wrong, say so explicitly in the corrective commit message with evidence, do not silently ignore it.

## KNOWN_CONTEXT
Raised automatically by scripts/status-remediation-tick.py (classification: genuine_audit_fail, reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race.). Full finding excerpt:
AUDIT: FAIL
Objective Understood: Reviewed worker task 'rca-task-20260726-172016-mother-router-and-roster-persistent-memo' (risk tier: tier1) by reading the actual diff, not a self-report.
Standards Reviewed: AGENTS.md Operating Rule 7c structured audit protocol; risk-tier.py's deterministic tier classification.
Scope Confirmed: 
Evidence Recorded: This task produced no real work to review: the branch has zero commits beyond its base checkout (git log master..HEAD is empty, reflog shows only the initial worktree reset at task creation time), and PROGRESS.md explicitly lists 'Not started' under Completed with no items checked off. A naive `git diff master` against the live master branch appears to show a large deletion-heavy diff, but that is an artifact of master having since merged an unrelated PR (#101, 'consolidate 6 dispatch/status scripts') that this stale branch predates -- it is not this worker's diff and is unrelated to the 'mother-router-and-roster-persistent-memo' task scope. Per the standing NO-DUPLICATION rule, a claim of completion (or in this case, a task reaching review) must be backed by verified real code changes, which do not exist here. Issues found: Branch has n

## SUCCESS_CRITERIA
- `gh pr view 585 --repo FChecklist/compliance-tracker --json state` still shows OPEN and mergeable after the fix
- A new commit exists on the branch after 2026-07-27T04:21:01Z that addresses each listed issue
- The next AUDIT comment on this PR is AUDIT: PASS, not AUDIT: FAIL

## EXPECTED_OUTPUT
A real corrective commit pushed to https://github.com/FChecklist/compliance-tracker/pull/585's branch, and a checkpoint note summarizing which of the listed issues were fixed vs disputed (with evidence).

## CONSTRAINTS
Do not merge this PR yourself. Do not modify audit/review scripts to make the finding pass without a real code fix. Stay within the files the original PR touched plus whatever files the finding requires changing.

## COMPLEXITY_TIER
judgment
