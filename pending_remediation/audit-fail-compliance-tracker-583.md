<!-- DRAFTED BY scripts/status-remediation-tick.py at 2026-07-30T05:58:15.419036+00:00 -->
<!-- classification: genuine_audit_fail (judgment_needed) -->
<!-- reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race. -->
<!-- STATUS: drafted, needs assistant review before dispatch (not auto-dispatched) -->

## OBJECTIVE
Fix the real AUDIT: FAIL finding on open PR https://github.com/FChecklist/compliance-tracker/pull/583 (compliance-tracker/claude-control/projexa worker-review pipeline) so a re-review can pass, without touching unrelated code.

## SCOPE
Read the real AUDIT: FAIL comment body on https://github.com/FChecklist/compliance-tracker/pull/583 in full (`gh api repos/FChecklist/compliance-tracker/issues/583/comments`) and the real diff (`gh pr diff 583 --repo FChecklist/compliance-tracker`). Address every issue it lists with a real code change on the existing PR branch `worker/task-20260726-172000-hr-performance-error-handling---payroll`, not a new branch. Do not re-argue the finding -- if it is factually wrong, say so explicitly in the corrective commit message with evidence, do not silently ignore it.

## KNOWN_CONTEXT
Raised automatically by scripts/status-remediation-tick.py (classification: genuine_audit_fail, reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race.). Full finding excerpt:
AUDIT: FAIL
Objective Understood: Reviewed worker task 'rca-task-20260726-172000-hr-performance-error-handling---payroll' (risk tier: tier1) by reading the actual diff, not a self-report.
Standards Reviewed: AGENTS.md Operating Rule 7c structured audit protocol; risk-tier.py's deterministic tier classification.
Scope Confirmed: 
Evidence Recorded: This task has no actual diff to review: HEAD is identical to the merge-base with master (fa3d6fd), git status is clean with no untracked files, no task-related branch exists locally or on remote, and PROGRESS.md explicitly shows an empty Completed section with only a single unchecked 'Not started' item. The worker never began the HR performance error-handling/payroll RCA work despite the task reaching review, so there is nothing to approve or merge. Issues found: No commits exist on this branch beyond the shared master merge-base — zero code changes were made.; PROGRESS.md confirms the task was never started ('Not started', empty Completed section).; No PR, branch, or artifact for this task scope exists anywhere in the repo, consistent with the claim-only/zero-real-code failure mode called out in SUPERBOSS_DISPATCH_PROMPT.md.; Recommend a

## SUCCESS_CRITERIA
- `gh pr view 583 --repo FChecklist/compliance-tracker --json state` still shows OPEN and mergeable after the fix
- A new commit exists on the branch after 2026-07-27T04:22:24Z that addresses each listed issue
- The next AUDIT comment on this PR is AUDIT: PASS, not AUDIT: FAIL

## EXPECTED_OUTPUT
A real corrective commit pushed to https://github.com/FChecklist/compliance-tracker/pull/583's branch, and a checkpoint note summarizing which of the listed issues were fixed vs disputed (with evidence).

## CONSTRAINTS
Do not merge this PR yourself. Do not modify audit/review scripts to make the finding pass without a real code fix. Stay within the files the original PR touched plus whatever files the finding requires changing.

## COMPLEXITY_TIER
judgment
