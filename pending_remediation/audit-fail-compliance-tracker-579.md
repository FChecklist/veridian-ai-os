<!-- DRAFTED BY scripts/status-remediation-tick.py at 2026-07-30T05:58:15.419329+00:00 -->
<!-- classification: genuine_audit_fail (judgment_needed) -->
<!-- reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race. -->
<!-- STATUS: drafted, needs assistant review before dispatch (not auto-dispatched) -->

## OBJECTIVE
Fix the real AUDIT: FAIL finding on open PR https://github.com/FChecklist/compliance-tracker/pull/579 (compliance-tracker/claude-control/projexa worker-review pipeline) so a re-review can pass, without touching unrelated code.

## SCOPE
Read the real AUDIT: FAIL comment body on https://github.com/FChecklist/compliance-tracker/pull/579 in full (`gh api repos/FChecklist/compliance-tracker/issues/579/comments`) and the real diff (`gh pr diff 579 --repo FChecklist/compliance-tracker`). Address every issue it lists with a real code change on the existing PR branch `worker/task-20260726-171939-delegation-expiry-enforcement-audit---te`, not a new branch. Do not re-argue the finding -- if it is factually wrong, say so explicitly in the corrective commit message with evidence, do not silently ignore it.

## KNOWN_CONTEXT
Raised automatically by scripts/status-remediation-tick.py (classification: genuine_audit_fail, reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race.). Full finding excerpt:
AUDIT: FAIL
Objective Understood: Reviewed worker task 'Delegation expiry enforcement audit + test' (risk tier: tier2) by reading the actual diff, not a self-report.
Standards Reviewed: AGENTS.md Operating Rule 7c structured audit protocol; risk-tier.py's deterministic tier classification.
Scope Confirmed:  PROGRESS.md                                        |  65 ++-----
 ...LEGATION_EXPIRY_ENFORCEMENT_AUDIT_2026-07-26.md | 194 +++++++++++++++++++++
 ai-os/boss/ACTIVE-CLAIMS.yaml                      |  37 ++++
 src/lib/services/approval-workflow-service.test.ts |  43 +++++
 src/lib/services/approval-workflow-service.ts      |  19 +-
 src/lib/services/delegation-service.test.ts        |  40 ++++-
 src/lib/services/delegation-service.ts             |  21 ++-
 .../services/erp-payment-entries-service.test.ts   |  27 +++
 src/lib/services/erp-payment-entries-service.ts    |  24 ++-
 9 files changed, 411 insertions(+), 59 deletions(-)
Evidence Recorded: The refactor (resolveDelegatedAuthority extraction) and test coverage for expiry/revocation are solid, but wiring isDelegated() into decideApprovalStep() and decidePaymentEntry() turns a previously dormant schema gap into a live, exploi

## SUCCESS_CRITERIA
- `gh pr view 579 --repo FChecklist/compliance-tracker --json state` still shows OPEN and mergeable after the fix
- A new commit exists on the branch after 2026-07-26T18:17:29Z that addresses each listed issue
- The next AUDIT comment on this PR is AUDIT: PASS, not AUDIT: FAIL

## EXPECTED_OUTPUT
A real corrective commit pushed to https://github.com/FChecklist/compliance-tracker/pull/579's branch, and a checkpoint note summarizing which of the listed issues were fixed vs disputed (with evidence).

## CONSTRAINTS
Do not merge this PR yourself. Do not modify audit/review scripts to make the finding pass without a real code fix. Stay within the files the original PR touched plus whatever files the finding requires changing.

## COMPLEXITY_TIER
judgment
