<!-- DRAFTED BY scripts/veridian_remediation_dispatcher.py at 2026-07-26T17:10:53.786878+00:00 -->
<!-- classification: genuine_audit_fail (judgment_needed) -->
<!-- reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race. -->
<!-- STATUS: drafted, needs assistant review before dispatch (not auto-dispatched) -->

## OBJECTIVE
Fix the real AUDIT: FAIL finding on open PR https://github.com/FChecklist/claude-control/pull/80 (compliance-tracker/claude-control/projexa worker-review pipeline) so a re-review can pass, without touching unrelated code.

## SCOPE
Read the real AUDIT: FAIL comment body on https://github.com/FChecklist/claude-control/pull/80 in full (`gh api repos/FChecklist/claude-control/issues/80/comments`) and the real diff (`gh pr diff 80 --repo FChecklist/claude-control`). Address every issue it lists with a real code change on the existing PR branch `worker/task-20260726-083833-build-interactive-session-write-gate--re`, not a new branch. Do not re-argue the finding -- if it is factually wrong, say so explicitly in the corrective commit message with evidence, do not silently ignore it.

## KNOWN_CONTEXT
Raised automatically by scripts/veridian_remediation_dispatcher.py (classification: genuine_audit_fail, reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race.). Full finding excerpt:
AUDIT: FAIL
Objective Understood: Reviewed worker task 'Write-gate round 4: argv-position fix + task-registry cross-reference (adopted)' (risk tier: tier1) by reading the actual diff, not a self-report.
Standards Reviewed: AGENTS.md Operating Rule 7c structured audit protocol; risk-tier.py's deterministic tier classification.
Scope Confirmed:  ai-os/OWNER_DIRECTIVES/PROTOCOL_OWNER_AI.yaml      | 285 ++++++++-
 .../interactive-session-guard.bashrc-snippet       | 693 +++++++++++++++++++++
 tests/interactive_session_guard_test.sh            | 642 +++++++++++++++++++
 tests/write_gate_test.py                           |  39 ++
 4 files changed, 1658 insertions(+), 1 deletion(-)
Evidence Recorded: This round-4 diff (PROTOCOL_OWNER_AI.yaml A15/A16 rewrite, the bashrc-snippet guard, and its two test files) genuinely closes the argv-position bypass it targets and adds a plausible task-registry cross-reference for the cgroup-forgery concern, with honest disclosure of several known limitations -- but the detection layer for both git and gh still matches subcommands by literal token name only, which misses the standard, well-documented alias features of both real binaries. `git -c alias.wip=

## SUCCESS_CRITERIA
- `gh pr view 80 --repo FChecklist/claude-control --json state` still shows OPEN and mergeable after the fix
- A new commit exists on the branch after 2026-07-26T12:32:05Z that addresses each listed issue
- The next AUDIT comment on this PR is AUDIT: PASS, not AUDIT: FAIL

## EXPECTED_OUTPUT
A real corrective commit pushed to https://github.com/FChecklist/claude-control/pull/80's branch, and a checkpoint note summarizing which of the listed issues were fixed vs disputed (with evidence).

## CONSTRAINTS
Do not merge this PR yourself. Do not modify audit/review scripts to make the finding pass without a real code fix. Stay within the files the original PR touched plus whatever files the finding requires changing.

## COMPLEXITY_TIER
judgment
