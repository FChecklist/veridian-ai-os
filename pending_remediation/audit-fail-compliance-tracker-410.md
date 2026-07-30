<!-- DRAFTED BY scripts/veridian_remediation_dispatcher.py at 2026-07-26T17:20:50.016873+00:00 -->
<!-- classification: genuine_audit_fail (judgment_needed) -->
<!-- reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race. -->
<!-- STATUS: drafted, needs assistant review before dispatch (not auto-dispatched) -->

## OBJECTIVE
Fix the real AUDIT: FAIL finding on open PR https://github.com/FChecklist/compliance-tracker/pull/410 (compliance-tracker/claude-control/projexa worker-review pipeline) so a re-review can pass, without touching unrelated code.

## SCOPE
Read the real AUDIT: FAIL comment body on https://github.com/FChecklist/compliance-tracker/pull/410 in full (`gh api repos/FChecklist/compliance-tracker/issues/410/comments`) and the real diff (`gh pr diff 410 --repo FChecklist/compliance-tracker`). Address every issue it lists with a real code change on the existing PR branch `dependabot/npm_and_yarn/eslint-10.7.0`, not a new branch. Do not re-argue the finding -- if it is factually wrong, say so explicitly in the corrective commit message with evidence, do not silently ignore it.

## KNOWN_CONTEXT
Raised automatically by scripts/veridian_remediation_dispatcher.py (classification: genuine_audit_fail, reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race.). Full finding excerpt:
AUDIT: FAIL
Objective Understood: Dependabot major version bump of eslint from 9.39.5 to 10.7.0.
Standards Reviewed: Did not trust the PRs own stale CI (a lockfile mismatch was masking the real result). Ran a real bun install against a genuinely reinstalled tree on this exact commit, then ran bun run lint for real (the actual command the required Lint CI check runs).
Scope Confirmed: Found and fixed a separate real problem first: Dependabots package.json bump was never accompanied by a bun.lock update, so bun install --frozen-lockfile failed before any check ever ran (masking the real result behind a misleading error). Regenerated bun.lock and pushed it so CI now reflects reality. The REAL result: bun run lint crashes hard -- TypeError: contextOrFilename.getFilename is not a function, thrown by eslint-plugin-react (v7.37.5, bundled via eslint-config-next 16.1.1) while evaluating react/no-direct-mutation-state. ESLint 9/10 removed/changed the legacy context.getFilename() API that eslint-plugin-reacts internal React-version-detector still calls. Confirmed there is no newer eslint-plugin-react release that fixes this (bun add eslint-plugin-react@latest still resolves to 7.37.5) and es

## SUCCESS_CRITERIA
- `gh pr view 410 --repo FChecklist/compliance-tracker --json state` still shows OPEN and mergeable after the fix
- A new commit exists on the branch after 2026-07-21T15:55:17Z that addresses each listed issue
- The next AUDIT comment on this PR is AUDIT: PASS, not AUDIT: FAIL

## EXPECTED_OUTPUT
A real corrective commit pushed to https://github.com/FChecklist/compliance-tracker/pull/410's branch, and a checkpoint note summarizing which of the listed issues were fixed vs disputed (with evidence).

## CONSTRAINTS
Do not merge this PR yourself. Do not modify audit/review scripts to make the finding pass without a real code fix. Stay within the files the original PR touched plus whatever files the finding requires changing.

## COMPLEXITY_TIER
judgment
