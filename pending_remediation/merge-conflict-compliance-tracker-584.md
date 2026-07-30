<!-- DRAFTED BY scripts/status-remediation-tick.py at 2026-07-30T05:58:15.422861+00:00 -->
<!-- classification: real_merge_conflict (judgment_needed) -->
<!-- reason: mergeStateStatus=DIRTY: a real content conflict against the base branch, not a transient state -- requires resolving actual conflicting changes, which is a judgment call this dispatcher must not make. -->
<!-- STATUS: drafted, needs assistant review before dispatch (not auto-dispatched) -->

## OBJECTIVE
Resolve the real merge conflict blocking open PR https://github.com/FChecklist/compliance-tracker/pull/584 against its base branch so it can merge cleanly, preserving both sides' real intent.

## SCOPE
Fetch the real base branch, run `git merge-base` / rebase the PR branch `worker/task-20260726-171420-phase5-browser-execution` onto the current base, and resolve every real conflicting hunk by reading both sides' actual changes (not by blindly picking one side). Push the resolved branch back to the same PR.

## KNOWN_CONTEXT
Raised automatically by scripts/status-remediation-tick.py (classification: real_merge_conflict, mergeStateStatus=DIRTY as of the triggering LIVE_STATUS run). This is a real content conflict, not a transient GitHub state -- confirmed by classify_merge_conflict() before this prompt was drafted.

## SUCCESS_CRITERIA
- `gh pr view 584 --repo FChecklist/compliance-tracker --json mergeStateStatus` returns CLEAN (not DIRTY) after the fix
- No test or check that was passing before the resolve now fails

## EXPECTED_OUTPUT
A real conflict-resolution commit pushed to https://github.com/FChecklist/compliance-tracker/pull/584's branch, with a checkpoint note explaining how each conflicting hunk was resolved and why.

## CONSTRAINTS
Do not merge this PR yourself once conflicts are resolved -- that is the normal supervisor review path's job, not this corrective task's. Do not force-push over the other side's real changes; every real change from both branches must be preserved or explicitly, visibly dropped with a stated reason.

## COMPLEXITY_TIER
judgment
