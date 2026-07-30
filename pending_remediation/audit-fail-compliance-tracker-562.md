<!-- DRAFTED BY scripts/veridian_remediation_dispatcher.py at 2026-07-26T06:20:50.526754+00:00 -->
<!-- classification: genuine_audit_fail (judgment_needed) -->
<!-- reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race. -->
<!-- STATUS: drafted, needs assistant review before dispatch (not auto-dispatched) -->

## OBJECTIVE
Fix the real AUDIT: FAIL finding on open PR https://github.com/FChecklist/compliance-tracker/pull/562 (compliance-tracker/claude-control/projexa worker-review pipeline) so a re-review can pass, without touching unrelated code.

## SCOPE
Read the real AUDIT: FAIL comment body on https://github.com/FChecklist/compliance-tracker/pull/562 in full (`gh api repos/FChecklist/compliance-tracker/issues/562/comments`) and the real diff (`gh pr diff 562 --repo FChecklist/compliance-tracker`). Address every issue it lists with a real code change on the existing PR branch `worker/task-20260726-043023-phase4-defense-in-depth-prompt-security`, not a new branch. Do not re-argue the finding -- if it is factually wrong, say so explicitly in the corrective commit message with evidence, do not silently ignore it.

## KNOWN_CONTEXT
Raised automatically by scripts/veridian_remediation_dispatcher.py (classification: genuine_audit_fail, reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race.). Full finding excerpt:
AUDIT: FAIL
Objective Understood: Reviewed worker task 'phase4-defense-in-depth-prompt-security-red' (risk tier: tier2) by reading the actual diff, not a self-report.
Standards Reviewed: AGENTS.md Operating Rule 7c structured audit protocol; risk-tier.py's deterministic tier classification.
Scope Confirmed:  PROGRESS.md                                        |  74 ++++----
 ...EFENSE_IN_DEPTH_TOOL_EVALUATION_2026-07-26.yaml | 188 +++++++++++++++++++++
 ai-os/boss/ACTIVE-CLAIMS.yaml                      |  63 +++++++
 scripts/defense-in-depth-smoke-test.ts             |  94 +++++++++++
 scripts/red-team-prompt-security.ts                |  35 ++++
 src/lib/prompt-security/defense-in-depth.test.ts   |  37 ++++
 src/lib/prompt-security/defense-in-depth.ts        | 117 +++++++++++++
 src/lib/prompt-security/index.ts                   |  12 ++
 .../layer1-input-sanitization.test.ts              |  57 +++++++
 .../prompt-security/layer1-input-sanitization.ts   | 118 +++++++++++++
 .../layer2-system-prompt-hardening.test.ts         |  23 +++
 .../layer2-system-prompt-hardening.ts              |  34 ++++
 .../layer3-runtime-guardrails.test.ts              |  32 ++++
 .../prompt-security/la

## SUCCESS_CRITERIA
- `gh pr view 562 --repo FChecklist/compliance-tracker --json state` still shows OPEN and mergeable after the fix
- A new commit exists on the branch after 2026-07-26T04:59:23Z that addresses each listed issue
- The next AUDIT comment on this PR is AUDIT: PASS, not AUDIT: FAIL

## EXPECTED_OUTPUT
A real corrective commit pushed to https://github.com/FChecklist/compliance-tracker/pull/562's branch, and a checkpoint note summarizing which of the listed issues were fixed vs disputed (with evidence).

## CONSTRAINTS
Do not merge this PR yourself. Do not modify audit/review scripts to make the finding pass without a real code fix. Stay within the files the original PR touched plus whatever files the finding requires changing.

## COMPLEXITY_TIER
judgment
