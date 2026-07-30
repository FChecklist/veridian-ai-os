# SUPERSEDED -- do not execute against this plan

`BACKLOG_COMPLETION_PLAN_2026-07-27.json` and `BACKLOG_COMPLETION_PLAN_2026-07-27.md`
(sibling files in this directory) were produced at 2026-07-27T03:09 by the
untracked, pre-fix copy of `plan_backlog_completion.py` that used to live
directly in `/opt/veridian/ai-os/` -- before the SUCCESS_CRITERIA
re-verification fix landed in claude-control PR #102. Their
`ALREADY_DONE_STALE_STATUS` classifications trusted a PR number mentioned
anywhere in an rca-chain's checkpoint prose being merged as proof an issue
was done, with no check that the merged PR's real diff satisfied the
original task's own SUCCESS_CRITERIA. Executing against this frozen plan is
exactly what produced the 2026-07-27 mass-mislabeling incident (32 real
task.yaml files hand-mislabeled `status=superseded`/`completed`).

They are kept in place, unmodified, as the historical/forensic record of
what the pre-fix classifier actually produced -- not deleted.

**Do not execute or re-run anything against these two files.** Both
`/opt/veridian/ai-os/plan_backlog_completion.py` and
`/opt/veridian/ai-os/execute_backlog_plan.py` have been rewritten (2026-07-27,
same PR #102) to delegate entirely to the fixed, tested, git-tracked
`scripts/plan_backlog_completion.py` in the claude-control repo and to
regenerate a fresh, SUCCESS_CRITERIA-verified plan at execution time --
neither reads these frozen files anymore.

See:
- `ai-os/DEDUP_MISMATCH_MANUAL_REVIEW_2026-07-27.yaml` (claude-control repo) --
  real `--audit-report` run confirming 31 of the 32 already-superseded
  records did not actually qualify under the fixed classifier.
- claude-control PR #102 for the full root-cause fix and this supersession.
