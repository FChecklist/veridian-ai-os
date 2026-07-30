<!-- DRAFTED BY scripts/status-remediation-tick.py at 2026-07-30T05:58:15.417862+00:00 -->
<!-- classification: genuine_audit_fail (judgment_needed) -->
<!-- reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race. -->
<!-- STATUS: drafted, needs assistant review before dispatch (not auto-dispatched) -->

## OBJECTIVE
Fix the real AUDIT: FAIL finding on open PR https://github.com/FChecklist/claude-control/pull/91 (compliance-tracker/claude-control/projexa worker-review pipeline) so a re-review can pass, without touching unrelated code.

## SCOPE
Read the real AUDIT: FAIL comment body on https://github.com/FChecklist/claude-control/pull/91 in full (`gh api repos/FChecklist/claude-control/issues/91/comments`) and the real diff (`gh pr diff 91 --repo FChecklist/claude-control`). Address every issue it lists with a real code change on the existing PR branch `worker/task-20260726-162246-resolve-pr89-merge-conflict--phase-2-pol`, not a new branch. Do not re-argue the finding -- if it is factually wrong, say so explicitly in the corrective commit message with evidence, do not silently ignore it.

## KNOWN_CONTEXT
Raised automatically by scripts/status-remediation-tick.py (classification: genuine_audit_fail, reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race.). Full finding excerpt:
AUDIT: FAIL
Objective Understood: Reviewed worker task 'Resolve PR89 merge conflict (Phase 2 policy unification)' (risk tier: tier1) by reading the actual diff, not a self-report.
Standards Reviewed: AGENTS.md Operating Rule 7c structured audit protocol; risk-tier.py's deterministic tier classification.
Scope Confirmed:  pr89-work | 1 +
 1 file changed, 1 insertion(+)
Evidence Recorded: The task's actual goal (resolve PR #89's merge conflict in ai-os/MASTER_INDEX.yaml) was genuinely accomplished and independently verified via gh api -- PR #89's merge commit ffa86b8 is a real, sensible combination of both sides' registry text and PR #89 now reports mergeable_state=clean -- but that work was delivered by pushing directly to PR #89's own head branch on GitHub, not through this diff. The diff actually presented for merge into this task's branch is unrelated debris: it adds pr89-work as a git submodule/gitlink (mode 160000) with no corresponding .gitmodules entry, an accidental byproduct of the worker's scratch clone directory getting swept into an automated checkpoint commit. Merging this diff as-is would introduce a dangling, unmapped gitlink into claude-control's master with no funct

## SUCCESS_CRITERIA
- `gh pr view 91 --repo FChecklist/claude-control --json state` still shows OPEN and mergeable after the fix
- A new commit exists on the branch after 2026-07-26T16:27:47Z that addresses each listed issue
- The next AUDIT comment on this PR is AUDIT: PASS, not AUDIT: FAIL

## EXPECTED_OUTPUT
A real corrective commit pushed to https://github.com/FChecklist/claude-control/pull/91's branch, and a checkpoint note summarizing which of the listed issues were fixed vs disputed (with evidence).

## CONSTRAINTS
Do not merge this PR yourself. Do not modify audit/review scripts to make the finding pass without a real code fix. Stay within the files the original PR touched plus whatever files the finding requires changing.

## COMPLEXITY_TIER
judgment
