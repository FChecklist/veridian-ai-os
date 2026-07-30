# Pending Owner Review -- corrected 2026-07-28T03:20:00Z

The orchestrator's automated PR-search had a real bug (wrong repo assumed
for cross-repo work, and GitHub's fuzzy PR search missed valid results) --
every item below was independently re-verified by hand via direct PR/audit
lookups, not trusted from the orchestrator's own log.

## MERGED (real, verified via mergedAt)
- projexa PR #57 -- Scope-of-Works revision/variation UI (auto-merged by
  the standard supervisor pipeline, tier1+PASS)
- compliance-tracker PR #605 -- Scope-of-Works schema companion (tier1+PASS)
- projexa PR #59 -- Full VERIDIAN module chain wired into PROJEXA chat
  (tier1+PASS; had a real merge conflict with main from other same-day
  merges, resolved and re-merged)

## NEEDS OWNER REVIEW (tier2, real PASS verdict, correctly not auto-merged)
- projexa PR #58 -- Work Progress Report (real column spec built: Prev/
  Current/Total for Amt+Percentage, reuses existing PWA offline queue)

## NEEDS A REAL FIX (FAIL verdict, do not merge as-is)
- compliance-tracker PR #610 -- Sales Pipeline dashboard: real FAIL,
  medium severity. Real work present (schema, service, route, UI, tests
  all real) but audit found issues -- read the full verdict via
  `gh api repos/FChecklist/compliance-tracker/issues/610/comments`
  before deciding whether to dispatch a fix or reject.
- compliance-tracker PR #606 -- reporting_module re-audit report itself:
  real FAIL, medium severity, even though it's a documentation-only PR --
  the audit report's own substance was flagged. Read the full verdict
  before resubmitting.
- projexa PR #60 -- Company/Dept/Project dashboard hierarchy: real FAIL,
  medium severity, tier1. Real architecture confirmed sound by the
  auditor but specific findings need a fix. This task's own PROGRESS.md
  also flags an unresolved compliance-tracker companion API dependency
  (category-distribution charts will 502 without it) that needs an
  explicit Owner/supervisor decision on whether to push it.

## STILL BEING AUDITED (fresh audits triggered 2026-07-28 03:13-03:15 UTC)
- compliance-tracker PR #604 -- TET engine increment 1
- compliance-tracker PR #607 -- VERI ERP Product-chain bug fix
- compliance-tracker PR #608 -- BoQ list/activities line-item enrichment
  (real companion work found during item 4's dispatch, not originally
  planned -- worth understanding what it covers before merge)
- compliance-tracker PR #609 -- Full VERIDIAN module chain API (the
  compliance-tracker side of PR #59's projexa work)
Check these again -- audits typically take 15-90 min for substantial diffs.

## STILL RUNNING (real work in progress, not stalled)
- functionality_completion audit (task-20260727-153100) -- long real audit,
  still dispatching Explore sub-agents to verify PRs #591/#592/#593
- Backlog items not yet dispatched: Permits/Drawings/Documents/MoMs,
  Manpower/Material/Budget/Schedule, Design Studio timesheets -- see
  /opt/veridian/ai-os/PROSPECT_GAP_BACKLOG_2026-07-28.md for full spec

## Real infrastructure issue found and fixed this session
Server's Claude Code OAuth session expired ~17:58 UTC 2026-07-27, causing
a cascading crash-loop across every new worker dispatch for ~1 hour.
Root cause: `~/.claude/.credentials.json` was left with empty
access/refresh tokens after the expiry, and `claude -p` (headless mode)
requires this file populated -- the CLAUDE_CODE_OAUTH_TOKEN env var alone
was not sufficient for that invocation path. Fixed by writing the Owner's
freshly-generated `claude setup-token` value into that file directly.
All crashed workers were restarted from their real checkpoints, not from
scratch.

# Pending Owner Review -- session started 2026-07-28T03:36:57.118467+00:00

## Fix PR #610 RLS gap (Sales Pipeline dashboard)
- task_id: task-20260728-032915-fix-pr-610-rls-gap-on-crm-sales-targets
- repo: compliance-tracker
- PR: none found
- reason: no PR found -- worker may have failed or not opened one

## Fix PR #60 dependency + error-state + pagination gaps
- task_id: task-20260728-032920-fix-pr-60-dependency---error-state---pag
- repo: projexa
- PR: none found
- reason: no PR found -- worker may have failed or not opened one

## Project records: Permits, Drawings&3D, Documents, MoMs (PROJEXA)
- task_id: none
- repo: projexa
- PR: none found
- reason: dispatch itself failed -- see status log

## Resource management: Manpower, Material, Budget, Schedule (PROJEXA)
- task_id: task-20260728-041200-resource-management--manpower--material
- repo: projexa
- PR: none found
- reason: no PR found -- worker may have failed or not opened one

## Design Studio timesheets: designer-wise cost analysis + KPI approval
- task_id: task-20260728-043316-design-studio-timesheets--designer-wise
- repo: compliance-tracker
- PR: #613
- reason: tier2/judgment -- needs Owner sign-off

## Verify Excel BoQ importer against real prospect file structure
- task_id: none
- repo: compliance-tracker
- PR: none found
- reason: dispatch itself failed -- see status log

# Pending Owner Review -- session started 2026-07-28T11:10:28.393564+00:00

## Fix PR #610 RLS gap (Sales Pipeline dashboard)
- task_id: task-20260728-032915-fix-pr-610-rls-gap-on-crm-sales-targets
- repo: compliance-tracker
- PR: none found
- reason: no PR found -- worker may have failed or not opened one

## Fix PR #60 dependency + error-state + pagination gaps
- task_id: task-20260728-032920-fix-pr-60-dependency---error-state---pag
- repo: projexa
- PR: none found
- reason: no PR found -- worker may have failed or not opened one

## Project records: Permits, Drawings&3D, Documents, MoMs (PROJEXA)
- task_id: none
- repo: projexa
- PR: none found
- reason: dispatch itself failed -- see status log

## Resource management: Manpower, Material, Budget, Schedule (PROJEXA)
- task_id: none
- repo: projexa
- PR: none found
- reason: dispatch itself failed -- see status log

## Design Studio timesheets: designer-wise cost analysis + KPI approval
- task_id: none
- repo: compliance-tracker
- PR: none found
- reason: dispatch itself failed -- see status log

## Verify Excel BoQ importer against real prospect file structure
- task_id: none
- repo: compliance-tracker
- PR: none found
- reason: dispatch itself failed -- see status log
