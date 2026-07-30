<!-- DRAFTED BY scripts/veridian_remediation_dispatcher.py at 2026-07-26T17:20:50.016720+00:00 -->
<!-- classification: genuine_audit_fail (judgment_needed) -->
<!-- reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race. -->
<!-- STATUS: drafted, needs assistant review before dispatch (not auto-dispatched) -->

## OBJECTIVE
Fix the real AUDIT: FAIL finding on open PR https://github.com/FChecklist/compliance-tracker/pull/484 (compliance-tracker/claude-control/projexa worker-review pipeline) so a re-review can pass, without touching unrelated code.

## SCOPE
Read the real AUDIT: FAIL comment body on https://github.com/FChecklist/compliance-tracker/pull/484 in full (`gh api repos/FChecklist/compliance-tracker/issues/484/comments`) and the real diff (`gh pr diff 484 --repo FChecklist/compliance-tracker`). Address every issue it lists with a real code change on the existing PR branch `worker/task-20260719-140432-smoke-test--verify-glm-5-2-proxy-routing`, not a new branch. Do not re-argue the finding -- if it is factually wrong, say so explicitly in the corrective commit message with evidence, do not silently ignore it.

## KNOWN_CONTEXT
Raised automatically by scripts/veridian_remediation_dispatcher.py (classification: genuine_audit_fail, reason: No audit-check run started before the AUDIT verdict comment existed -- this is a real, correlated review finding, not a CI-timing race.). Full finding excerpt:
AUDIT: FAIL
Objective Understood: PRs own PROGRESS.md/title describe this as a smoke test verifying GLM-5.2 proxy routing + a README.md marker line + confirming no CI quality-gate is broken by that change -- a benign diagnostic task. But the PRs actual file diff also includes drizzle/0001_wakeful_reptil.sql (6,080 lines) and a matching drizzle/meta/_journal.json entry, which the PRs own PROGRESS.md text never mentions writing or intending.
Standards Reviewed: Compared the PRs stated work (PROGRESS.md) against its actual diff. Read drizzle/0001_wakeful_reptil.sql in full: it is an auto-generated drizzle-kit migration that recreates the ENTIRE current schema from scratch (CREATE SCHEMA platform; then bare CREATE TYPE ... AS ENUM for every enum and CREATE TABLE for every table in schema.ts, all WITHOUT IF NOT EXISTS/exception guards) -- exactly what drizzle-kit generates when it believes only migration 0000 has ever been applied (which is what drizzle/meta/_journal.json says: idx 0 only, tag 0000_clammy_may_parker). This session independently confirmed earlier that _journal.json is stale/frozen at 0000 while 250+ real migration files (0001 through 0253) already exist as files in drizz

## SUCCESS_CRITERIA
- `gh pr view 484 --repo FChecklist/compliance-tracker --json state` still shows OPEN and mergeable after the fix
- A new commit exists on the branch after 2026-07-21T15:20:37Z that addresses each listed issue
- The next AUDIT comment on this PR is AUDIT: PASS, not AUDIT: FAIL

## EXPECTED_OUTPUT
A real corrective commit pushed to https://github.com/FChecklist/compliance-tracker/pull/484's branch, and a checkpoint note summarizing which of the listed issues were fixed vs disputed (with evidence).

## CONSTRAINTS
Do not merge this PR yourself. Do not modify audit/review scripts to make the finding pass without a real code fix. Stay within the files the original PR touched plus whatever files the finding requires changing.

## COMPLEXITY_TIER
judgment
