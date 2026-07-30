<!-- DRAFTED BY scripts/veridian_remediation_dispatcher.py at 2026-07-26T19:01:36.205384+00:00 -->
<!-- classification: merge_failed_real_conflict (judgment_needed) -->
<!-- reason: Checkpoint note says a Superboss-approved merge attempt failed, but a fresh check now shows mergeStateStatus=DIRTY -- a real conflict exists, not a transient failure; retrying the merge would not succeed and is not attempted. -->
<!-- STATUS: drafted, needs assistant review before dispatch (not auto-dispatched) -->

## OBJECTIVE
Resolve the real merge conflict now blocking https://github.com/FChecklist/compliance-tracker/pull/573, previously Superboss-approved but failed to merge.

## SCOPE
Same as any real merge-conflict corrective task: rebase/resolve the real conflicting content on https://github.com/FChecklist/compliance-tracker/pull/573, then push.

## KNOWN_CONTEXT
task task-20260726-171950-preview-deployment-spot-check checkpoint note: tier1, Superboss-approved, but the merge itself FAILED (gh pr view confirms state=OPEN, mergedAt=; see supervisor.log) — needs manual attention, NOT actually merged: https://github.com/FChecklist/compliance-tracker/pull/573. Fresh check shows mergeStateStatus=DIRTY.

## SUCCESS_CRITERIA
- `gh pr view https://github.com/FChecklist/compliance-tracker/pull/573 --json mergeStateStatus` returns CLEAN

## EXPECTED_OUTPUT
A real conflict-resolution commit pushed to the PR branch.

## CONSTRAINTS
Do not merge this PR yourself once resolved.

## COMPLEXITY_TIER
judgment
