# VERIDIAN Parallel Work Status — Live Tracking Document

*Created 2026-07-30 by claude-code-cli agent at Owner's explicit request for a single common documentation location covering all parallel workstreams. Update this file in place on every material status change rather than creating a new dated file — this is meant to be the one place to check, not another stale snapshot.*

## How to read this doc

Each workstream below lists: what it is, why it matters, current real state (checked via `gh pr view`/`gh pr checks`, not assumed), and the dispatched agent tracking it (if any). "Real state" timestamps are UTC.

---

## Workstream A: SAP-equivalent report backlog (Task #17)

Goal: close all 14 BUILD_NEW SAP-equivalent reports for the PROJEXA/compliance-tracker prospect.

| Report | PR | State (as of 2026-07-30 ~12:15 UTC) | Notes |
|---|---|---|---|
| FI-AR-004, SD-002, FI-AP-007, FI-AP-008, SD-007, FI-AA-006, FI-AR-006, FI-AP-006 | #636, #629/#638, #642, #646, #644, #648, #645, #651 | **MERGED** | 8 of 14 done |
| Journal-fix (infra, found along the way) | #650 | **MERGED** | Fixed a silently-never-applied migration |
| FI-AP-005 | #637 | CI-green (7/7 required checks), awaiting independent audit | Agent `a5beb2b0865984236` dispatched auditor. **Migration reassigned to 0285** (was racing #630/#633/#647 on 0283) |
| FI-GL-007 | #647 | Migration reassigned to 0286, fresh push just reset CI to pending (~12:15 UTC) | Agent `adfb4c076e69052e3`. Also root-caused and fixed a real, 11+ day standing Promptfoo Evals systemic failure (shared Groq rate-limit contention across concurrent branch CI runs) — separately valuable beyond this one PR |
| SD-006 | #652 | **Rebased clean twice** (main advanced mid-task, second real idx-278 collision with `11db691a`'s Stage-12 dispatch-outcomes migration) — final tip `d587fcb4`, `mergeable=MERGEABLE`, all required checks pass (Lint/Type Check/Build/Guardrail Presence/Asset Registry Coverage/Unit Tests) except `audit-check`, awaiting independent Rule 7c audit (not posted by this task per its own scope). Non-required `Promptfoo Evals` also fails (pre-existing Groq infra issue, confirmed unrelated) | Agent `a90e5f1c49c55d85a`. **Migration kept as `0302_sd006_sales_by_material_service_type_report_definition.sql`, journal idx 279** (verified free against freshly-fetched `origin/main` both times) |
| CO-006 | #653 | Rebased clean onto main (`0b6b9028`), `mergeable=MERGEABLE`, all required checks pass (Lint/Type Check/Build/Guardrail Presence/Asset Registry Coverage/Unit Tests) — only `audit-check` fails, awaiting independent Rule 7c audit | Agent `af8ae0cbdabd7b000` (2026-07-30 ~18:35 UTC). Migrations unchanged at **0288/0289/0292** — verified free against fresh `origin/main` journal (main's tip is 0301 with an unused 0286-0300 gap; no collision) |
| CO-006 re-rebase | #653 | **Rebased clean a second time** (task `task-20260731-045841-re-rebase-pr-653--drifted-back-to-confli`, 2026-07-31): drifted back to `CONFLICTING` after main gained one more merge (`11db691a`, #639 Stage-12 dispatch-outcomes) past the prior rebase's base. Real conflict was an idx-278 `drizzle/meta/_journal.json` tail collision (both #639 and CO-006's branch independently appended off the same base) plus an additive `ACTIVE-CLAIMS.yaml`/`report-catalog-service.ts` conflict (both resolved by keeping both sides' entries) and a rename/rename conflict on the branch's own internal 0280-0282→0288-0290 renumbering commit (git's linearized rebase dropped a prior merge-commit's file-rename resolution, requiring it to be reconstructed by hand). Final head `7ecfc9bc` (three doc-only follow-up commits logged this session after the rebase itself, `62c021ef` -> `b220ab9a` -> `d057fd4f` -> `7ecfc9bc`), migrations still **0288/0289/0292** (re-verified free against a freshly-fetched `origin/main` journal), `mergeable=MERGEABLE`, all 6 non-audit required checks pass (Lint/Type Check/Build/Guardrail Presence/Asset Registry Coverage/Unit Tests). Only failures: expected `audit-check` (7th required check, no verdict posted, per task scope) and non-required `Vercel` (build-rate-limit, confirmed not in branch-protection required-checks list, unrelated to this rebase) |
| HCM-006 | #654 | Conflict from #651 merge + real idx/number collision with #655 (both claimed 276) | Agent `a05ca7936d7a56302` — **reassigned to migration 0287** |
| CRM-007 | #655 | Rebased twice onto post-#654 (then post-#639) `origin/main` (head `fdf85095`), `mergeable=MERGEABLE`, all required checks pass except `audit-check` (stale pre-rebase `AUDIT: FAIL` comments from before either rebase -- a fresh independent audit is the next step, not posted by this task per its own scope) and non-required `Vercel` (build-rate-limit) | Task `task-20260730-183108-rebase-renumber-pr-655--crm-007--off-654`. Migration `0302_crm007_sales_rep_performance_report_definition.sql` kept (still free among real files on main), journal position renumbered twice: idx 278 (off #654's real idx-274 non-collision) then idx 279 (off a second real idx-278 collision with #639, which merged mid-task and claimed idx 278 first) |

## Workstream B: VERIDIAN_CONSOLIDATED_COMPLETION Phase 2 closure (Task #44)

Goal: close all remaining stages of the 13-stage Phase 2 plan — formal prerequisite gate for TWO_ENGINE_TASK's Phase 3 (Workstream C).

| Stage | PR | State (as of 2026-07-30 ~12:15 UTC) | Notes |
|---|---|---|---|
| Stage 9 (unified-search view) | #630 | CI-green (all required checks pass), independent audit dispatched (`ab819efac315e3d87`) | **Keeps migration 0283** (first to reach CI-green in the 4-way race) |
| Stage 10 (receptionist-tier task-status test coverage) | #631 | **MERGED** (2026-07-30T12:20:15Z) | No migration involved |
| Stage 11 (receptionist-tier notice-status) | #632 | Still OPEN as of 2026-07-31T03:19Z re-check | Agent `ad50a130b5b01d7e6` |
| Stage 12 (extend content_search to tasks) | #633 | **MERGED** (2026-07-30T12:56:15Z) | Agent `ae3bab1461e3a30bb` |
| Stage 12 (AI Dev Team dispatch persistent memory) | #634 vs #639 — confirmed real duplicate | **MERGED** — #634 confirmed CLOSED/not-merged (safe duplicate), #639 squash-merged as `11db691adb2b69e1eee1781a8804518247b91aa7` at 2026-07-31T03:18:58Z | Rebased clean onto `main`@`8aafc199` (reconstructed as single commit `e86457d7` after unresolvable rename/rename conflicts in the old branch history), all required checks green, pre-existing `AUDIT: PASS` honored per task scope |

**Migration number coordination note (2026-07-30 ~12:10 UTC):** a real 4-way collision was found on number `0283` across PRs #630/#633/#637/#647 (all independently landed on it after checking the same "next free" snapshot at nearly the same moment) — this is the exact race-condition class the collision-check script (Workstream E) is meant to eventually prevent, but doesn't yet catch in real time. Manually assigned: #630→0283 (kept, first CI-green), #633→0284, #637→0285, #647→0286. Separately, #654 and #655 both independently claimed `0276` — #654 reassigned to 0287.

**Correction (2026-07-30, later same day):** the "#630 keeps 0283" call above didn't hold — an independent audit (`AUDIT: FAIL`, severity high) found PR #637 still had its own `_journal.json` entry claiming idx 275/`0283` twelve minutes after PR 630's last push, with no ACTIVE-CLAIMS.yaml or PR-comment record confirming #637 had actually agreed to vacate the slot. Renumbered PR #630's migration `0283_content_search_view.sql` → `0302_content_search_view.sql` (verified free against a freshly-fetched `origin/main` `_journal.json` AND every one of the 71 open PRs' live head trees at the time, not just the 4 named in the original collision), rebased onto current `origin/main`, pushed as commit `784ab0f15c7d1ee950e8a180bb7d302a8225961a` on branch `task-20260729-120933-stage9-content-search-view`.

**Second re-rebase (2026-07-31, task `task-20260731-050057-re-rebase-pr-630--drifted-back-to-confli`):** PR #630 had drifted back to `CONFLICTING` — main advanced one more merge (#639) past the prior 0302 renumbering. File number `0302` itself was still free (no new collision), but main's own `0284_content_search_tasks` (#633, Stage 12, merged ahead of #630) had already extended `compliance.content_search` to a third `tasks` UNION ALL branch and now sits earlier in `drizzle/meta/_journal.json` than #630's newly-appended entry necessarily would. A plain re-apply of #630's original 2-branch `CREATE OR REPLACE VIEW` would have run after 0284 on a fresh `migrate()` and silently dropped the `tasks` branch — a real regression, not just a numbering formality (CI doesn't execute `drizzle-kit migrate` today, so this wouldn't have been caught by CI, only by a fresh-DB run later). Fixed by recreating `0302_content_search_view.sql` with the same 3-branch shape 0284 already established, making it idempotent-safe and order-independent regardless of which file a future `migrate()` run applies second. Rebased clean onto `origin/main`@`11db691a`, pushed as commit `c1a25aed81252e2ba0abad3b99802a382162fdde` on branch `task-20260729-120933-stage9-content-search-view`. Verified: `mergeable=MERGEABLE`, all required CI checks pass except the expected stale `audit-check` (left untouched per task scope — a separate task handles a fresh verdict).

**Still not complete (3 of 5 MERGED as of 2026-07-31T03:19Z).** Stages 10, 12/content_search, and 12/dispatch-persistent-memory are now MERGED. Stage 9 (#630) and Stage 11 (#632) remain OPEN — verified live via `gh pr view`, not assumed. Do not treat Phase 2 as done until those two also show MERGED.

## Workstream C: TWO_ENGINE_TASK Phase 3 / Core Kernel consolidation (Task #45)

**Status: real investigation complete, one concrete quick-win identified and being acted on.**

The Owner pushed back on the filed analysis's "PARTIAL, unbridged" verdict, citing `superboss-register.py`, a "4-layer AI orchestra," and existing AI routers as already-built infrastructure. A dedicated re-investigation (`acd5bf61e414c2ecb`) checked this claim against real code and found:

- **Policy Engine — STILL-TWO-SEPARATE-SYSTEMS.** superboss-register.sqlite's own `wiring_registry` claims a shared-citation bridge between the two implementations; checked against real source, that specific claim doesn't hold up (one file doesn't actually reference what the registry says it does).
- **Metadata Engine — still separate at runtime, but a real (narrow) bridge exists** at the schema-convention level: the same UTM field convention (`utm_source`/`utm_medium`/etc.) was deliberately applied across both the SQLite and Postgres metadata mechanisms.
- **Planning Engine — REAL FINDING, ACTIONABLE NOW.** A real integration between `plan_generator.py` and `resource_governor.py` was built earlier TODAY (staged in dated backup files from 08:06 UTC) but is **not currently deployed** to the live file (which is 3 days stale). Dispatched agent `ab311a6748e084ccf` to determine whether this was a deliberate rollback (real bug found — leave it) or a missed promotion (safe to deploy) and act accordingly, following the project's safe-edit discipline.
- **AI Orchestrator — Owner is substantively right.** "4-layer AI orchestra" = VAIOS Layer 1-4 (Platform→Org→Client→User model resolution), confirmed real, complete, live in production since Wave 45. This is genuinely built. However it serves only the product/end-user persona — zero connection to any Owner-ops script (`layer0_router.py`, Mother Router, `superboss-register.py`) — so it doesn't itself close the cross-persona kernel gap, even though it's solid infrastructure worth crediting more than the original analysis did.

**Net verdict:** more is built than the original "designed but not built" framing suggested, but the specific cross-persona bridges (Owner-side script ↔ product-side code) still don't exist for 3 of 4 candidates. Planning Engine is the one candidate where real, already-completed work just needs verifying/redeploying rather than building from scratch.

**Still blocked on Workstream B completing** before any formal Phase 3 implementation dispatch, per the analysis's own explicit statement.

## Workstream D: Broader stale-PR backlog (untriaged)

18 open PRs from earlier phases of this project (#604, #610, #618–#628, #635, #641, #643) are `DIRTY/CONFLICTING`, predate today's active threads, and have had zero attention this session. Real scope unknown until triaged.

### Update 2026-07-31 — 9 of the 18 triaged (#619–#628, excl. #618/#625 which don't exist in this range)

Task `task-20260731-035615-triage-9-stale-bookkeeping-prs--619-628` read every real diff/body for #619/#620/#621/#622/#623/#624/#626/#627/#628 (all confirmed docs/governance-bookkeeping only -- zero `src/`/`drizzle/` touched by any of the 9). Decisions, each with a real citation, no merges performed:

- **Closed #621** -- superseded by #623 (same misfiled-duplicate-task family): #623 found #621's own claim ("no PR exists yet against claude-control") was stale -- `claude-control#103` had already merged a day before #621 opened.
- **Closed #624** -- superseded by #628: #628 documents the identical `sap_reports.engine_track` classification (67 calculation/9 hybrid/4 workflow, 80 rows) with a durable audit-trail file (`ai-os/tasks/sap_mapping/PHASE_1_CLASSIFY.yaml`) and its own AUDIT: PASS comment, which #624 lacks.
- **Closed #627** -- moot: its only deliverable (an AUDIT: PASS comment on #624) already exists live on GitHub regardless of merge, and #624 itself is being closed anyway.
- **Rebased onto current `origin/main` and left CI-green for a separate audit** (all now `MERGEABLE`, all real CI checks pass, only the intentional `audit-check` gate is outstanding): **#619** (Phase-0-baseline close-out -- PR #615 is merged but main's `ACTIVE-CLAIMS.yaml` still showed it `active`), **#620** (ERP Helpdesk/PM/HR re-audit -- 2 real unresolved authorization gaps documented, not yet on main; also fixed a real Metadata Index Coverage Check failure), **#622** (periodic-checkpoint cgroup-throttle re-fix -- real fix independently confirmed merged in `claude-control#115`, just not yet recorded in this repo's registry), **#623** (the corrected/most-complete record of the misfiled-duplicate-task family), **#626** (independent `sap_reports` cross-reference audit, new artifact not yet on main), **#628** (most complete `engine_track` classification record).

9 of the 18 Workstream D PRs remain untriaged: #604, #610, #635, #641, #643, plus 4 more not yet identified in this pass.

## Workstream E: Migration-collision infrastructure fix (new, real, high-value)

A real bug in `scripts/check-migration-collision.mjs` was found while landing PR #647: it resolves its diff base via a possibly-stale local `main` git ref (confirmed stale on this server: pinned at an old commit while `origin/main` had moved on, because an old task worktree still has `main` checked out). This causes false signal — both missed real new collisions and flagged historical ones as new. Also confirmed NOT wired into any CI workflow today. Two real pre-existing collisions found already on `origin/main` itself (not from any single PR): number `0225` and number `0269`, each used by two different files.

Agent `a414557db9601f896` dispatched to: fix the script to prefer `origin/main`, add a `--base` override, wire it into CI as a real gate, and renumber the two pre-existing collisions with a journal fix. **This is expected to meaningfully reduce future collision cascades** like the ones documented in Workstream A/B above — flagged to that agent as a live, real-time illustration of exactly the problem it's fixing.

## Blocked items (not time-bound, require the Owner)

- Task #18 (authenticated PROJEXA adversarial testing) and Task #36 (Tenant B demo org) — both require entering a password to authenticate, which stays off-limits regardless of authorization.
- 6 decisions reserved by Phase 2's own plan (Part 5): which paused cron jobs resume, unified-search security model, a real alert channel, the 2026-08-05 policy date, per-unit+aggregate spend limits, a metadata-shape decision.

---

*Last updated: 2026-07-30 ~12:15 UTC, mid-session. Next update: when Workstream A/B agents report back, or when the Workstream C/E investigations land.*

## Update 2026-07-30 ~12:45 UTC

**Planning Engine (Workstream C) — REAL PROGRESS, now live.** The reuse-check integration ( wired into ) that was found staged-but-undeployed is now confirmed LIVE and verified working: a real  test recorded a genuine  on a new UMR row, and the previously-broken disk_io metric (which had also been silently reverted) now reports sane percentages instead of pegged 100%. Both files match git HEAD ( on ) exactly.

**New, separate, high-severity finding surfaced during that investigation:** live server scripts (, ) have been silently clobbered by an out-of-band overwrite at least twice today, plus a  collision between two concurrent sessions corrupting a commit message. This happened even AFTER git tracking was added this morning specifically to prevent this class of loss. Root cause not yet identified — a dedicated investigation is running (agent ), writing findings to . **This is a real, active risk to every other workstream in this doc** if it recurs while other agents are mid-edit on shared server paths — treat as high priority once the investigation lands.

## Update 2026-07-30 ~12:45 UTC

**Planning Engine (Workstream C) — REAL PROGRESS, now live.** The reuse-check integration (`plan_generator.check_reuse_before_dispatch()` wired into `resource_governor.py.submit()`) that was found staged-but-undeployed is now confirmed LIVE and verified working: a real `--submit` test recorded a genuine `reuse_check_result` on a new UMR row, and the previously-broken disk_io metric (which had also been silently reverted) now reports sane percentages instead of pegged 100%. Both files match git HEAD (`52c8367` on `main-clean`) exactly.

**New, separate, high-severity finding surfaced during that investigation:** live server scripts (`resource_governor.py`, `plan_generator.py`) have been silently clobbered by an out-of-band overwrite at least twice today, plus a `/tmp/commit_msg.txt` collision between two concurrent sessions corrupting a commit message. This happened even AFTER git tracking was added this morning specifically to prevent this class of loss. Root cause not yet identified — a dedicated investigation is running (agent `ae68fd94021a7e0c1`), writing findings to `/opt/veridian/ai-os/LIVE_SCRIPT_CLOBBERING_INVESTIGATION_2026-07-30.md`. **This is a real, active risk to every other workstream in this doc** if it recurs while other agents are mid-edit on shared server paths — treat as high priority once the investigation lands.

## Update 2026-07-30 ~13:05 UTC — clobbering investigation closed

**Root cause found and confirmed by direct evidence** (full writeup: `/opt/veridian/ai-os/LIVE_SCRIPT_CLOBBERING_INVESTIGATION_2026-07-30.md`): `/opt/veridian/scripts` is simultaneously the LIVE production path (re-executed every 30s by `resource_governor_tick_loop.sh`) and a shared git working tree with multiple divergent local branches. A plain `git checkout` in that directory rewrites every tracked file system-wide instantly, no lock, no warning — that was the actual clobbering mechanism (not cron, not systemd — both ruled out). Confirmed via reflog (3 branch checkouts in 20 minutes today) and a preserved backup file whose inode birth time matched a checkout event to the second.

**Fixed:** the two stale, divergent local branches (`main`, `reuse-check-enforcement-gate-phase7`) that could reproduce this were renamed (not deleted, fully reversible) to `archive/*-superseded-20260730-DO-NOT-CHECKOUT-LIVE`. Verified live files still match `main-clean` HEAD byte-for-byte after the rename.

**Two items correctly left as standing-convention flags rather than unilateral code fixes** (real judgment call, not indecision):
1. The structural hazard itself (one directory = live path + shared checkout) is unchanged — any future branch checkout here could reproduce this. Convention needed: never `git checkout`/`reset`/`pull` casually in `/opt/veridian/scripts`; use `git show <branch>:<file>` or a separate clone.
2. Flat, shared `/tmp` scratch paths are a live, active collision risk across concurrent sessions (confirmed: hundreds of generic-named scratch files from many sessions, no per-session subdirectory convention) — needs session-scoped `/tmp/<session-id>/` dirs as a standing practice, same pattern `node-gyp` already uses on this box.

This closes the immediate active risk to everything else in this document. The two remaining items are conventions for the Owner/future sessions to adopt, not code that needed writing.

## Update 2026-07-30 ~13:52 UTC — CRM gap analysis (Task #46) complete

Owner supplied a reference telecom-CRM product-documentation doc. Real gap analysis run against `compliance-tracker`'s actual CRM code (`crm-service.ts`, `crm-accounts-service.ts`, schema), framed generically per Owner's explicit instruction (find universal CRM gaps, not telecom-specific ones; don't touch our UI/UX/VERI Chat/flow).

**9 real, generic gaps identified, prioritized to close:**
1. Lead/deal source-attribution enum + expanded lead status set (currently 5-value, reference has 10)
2. Campaign entity (name/type/objective/date-range/budget) — currently zero campaign table exists
3. Project-team multi-user assignment (currently single `leadUserId` only, no junction table)
4. CRM-internal KPI dashboard — backend aggregation (`getSalesPipelineOverview()`) already real, just never rendered inside the CRM UI itself
5. Assignment/distribution dashboard + auto-assign-by-sharing-count (bulk reassign primitive exists, no allocation dashboard or auto-distribution logic)
6. Announcements (broadcast messaging) — `notifications` table is per-user only, no fan-out entity
7. CRM-specific import/export — exists for compliance/GST/bank-reconciliation, not for leads/contacts/accounts
8. Country/State/City cascading dropdowns — no master tables exist anywhere in the app (affects every address field, not just CRM)
9. Generalized resource-loan/return-tracking (the one telecom-specific pattern worth generalizing: BOM-borrow overdue-alert-tiers → extend `erpAssetMovements` with expected/actual return dates + tiered alerts, reusable for any industry's borrowed-asset tracking)

**Explicitly NOT building** (genuinely vertical/legacy-specific, correctly scoped out): the literal "network feasibility study" wrapper, PAN/GSTIN-on-Companies (already solved at a different entity), Form-16A tax certs, the 600-table Display Attributes toggle grid.

**Note on CRM-007**: the gap-analysis agent flagged "Sales Rep Performance Dashboard not found" as a discrepancy — this is expected, not a real problem. CRM-007 is PR #655, still open/unmerged as of this check; the agent correctly checked main HEAD.

**Dispatch plan**: given the current migration-number collision volatility across ~10 concurrent PRs, starting with the CRM-internal KPI dashboard (item 4) since it needs no new migration — reuses already-built backend aggregation. Schema-heavy items (1, 2, 3, 6, 8, 9) will be sequenced after PR #656 (the collision-check CI fix) merges, to reduce collision risk on new migrations.

## Update 2026-07-30 ~14:10 UTC — PM-platform feature-parity task registered (Task #47)

Owner supplied a detailed reverse-engineering exploration + 38-page companion PDF of a real cloud PM platform (confirmed as Zoho Projects — "Zoho Cliq"/"zohoprojects.com" referenced directly). Full field-level entity schemas extracted: Project (20 fields), Task (14 fields, self-referencing subtask hierarchy), Issue (18 fields — richer classification: Severity/Module/Classification/Reproducible/Flag, genuinely distinct from Task), TimeLog (15 fields, links to Project/Phase/TaskList/Task/Issue or none), User (8 fields, 3-way UserType enum: Portal/Client/Customer), WorkflowRule (8 fields, generic trigger catalog: Create/Edit/Delete/StatusChange/DueDate/Assignment/Comment/Time-based — not just Archive/Unarchive).

**Owner instruction**: replicate ALL features/modules/business-rules into BOTH compliance-tracker and PROJEXA-AI.COM, but use our own UI/UX/VERI Chat/flow, not the reference's. Zero gaps required. Same discipline as the CRM task (Task #46): real gap analysis first, build only real generic gaps, audit each via Rule 7c, document here.

**Real gap-analysis agent dispatched** (`aaab8b6db73a7098b`) covering both repos: Dashboard widgets, Projects (tabs/completion%/templates/groups/access-control), Users (5 sub-types), Collaboration/social-feed, Approvals, Tasks (subtasks+AI-suggest), Issues (18-field bug-tracking model), Phases/Milestones (auto-rollup completion%), Time Logs (weekly grid+billing), Timesheets (approval), Project-creation-form's 18 fields, Workflow-Rules automation engine. Supplemented mid-flight with the full field-level schema detail once the PDF was read.

**Not yet dispatched**: any actual build work — waiting on the gap analysis to land first, and for the current migration-collision volatility (Workstream A/B, ~10 concurrent PRs) to settle somewhat before adding more schema-heavy work to the same contested number range.

**Owner clarification 2026-07-30 ~14:15 UTC**: compliance-tracker and projexa are ONE system, zero duplication. compliance-tracker is the real backend; projexa is a thin front-end exposing the same modules via the existing callVeridian() API bridge. All Task #46/#47 gap-closing work happens ONCE in compliance-tracker; projexa work is limited to verifying/extending the bridge, never a parallel build.

## Governing principle for Tasks #45/#46/#47 (Owner framing, 2026-07-30 ~14:20 UTC)

All three tasks are ONE effort, not three separate initiatives: CRM feature-parity (#46) and PM-platform feature-parity (#47) are both contributions TO the Core Kernel/OWNER_ENGINE unification (#45), not parallel work. The standing philosophy: deterministic software/rules-and-logic is the first layer everywhere in this system; AI is an assistant layered on top, never the primary decision-maker. Every new capability built for #46/#47 (workflow-rules engine, phase roll-up math, auto-assignment logic, etc.) must be real deterministic code -- explicit rules, explicit state machines, explicit calculations -- matching the pattern already proven in the SAP-report work this session. Relayed to both active gap-analysis agents (CRM: ab0bda8c518abda7f, PM: aaab8b6db73a7098b) to shape their final recommendations.

## Update 2026-07-30 ~14:30 UTC — CRM gap analysis (Task #46) FINALIZED

Agent `ab0bda8c518abda7f` completed a second pass explicitly checking zero-duplication and deterministic-first-software compliance, with real file:line evidence throughout. All 10 recommendations confirmed compliant or tightened:

- **Zero new tables needed for**: Lead/Deal source attribution+status (additive columns on `crmLeads`/`crmOpportunities`), Items Master gaps (additive on `erpItems`/`erpItemGroups`), CRM KPI dashboard (zero schema, pure UI on existing `getSalesPipelineOverview()`), Assignment/auto-distribution dashboard (zero schema, `GROUP BY ownerId` count queries), Feasibility/BOM tracking (additive columns on existing `erpAssetMovements`), Settings Field Map (reuse existing GST-reconciliation import pattern), Country/State/City (static reference data, no table needed at all — just a shared constants file + component).
- **Genuinely new, no existing analog anywhere in the 600+ table schema**: Campaigns (new entity), Announcements (only the content table is new — delivery reuses existing `notifications` table + one new enum value + existing `metadata` jsonb column, explicitly designed to avoid a bespoke FK per notification type).
- **New junction table needed but following an existing convention**: Project team assignment — same shape as already-existing `pmsMeetingParticipants`/`userClientAccess`/`conversationParticipants` junction tables, not a novel pattern.
- **CRM Import/Export**: reuse existing generic `ingestionBatches` table (already org/file/status/count-shaped) rather than a new CRM-specific batch table.

**Deterministic-first confirmed for every item**, most notably: auto-assign-by-sharing-count is a plain least-loaded/round-robin SQL query (zero AI), feasibility overdue-tiers is date-bucketing SQL, announcement fan-out is deterministic insert-per-user, campaign scoring already exists as a pure formula (`marketing-engine.ts`). No recommendation implied an LLM-driven decision anywhere it wasn't already appropriately scoped that way.

**Next: dispatching real build work**, starting with the zero-schema-change items to avoid adding to the current migration-number contention (Workstream A/B still has ~8 concurrent PRs racing on migration numbers).

## Update 2026-07-30 ~15:10 UTC — PM-platform gap analysis (Task #47) FINALIZED

Agent `aaab8b6db73a7098b` completed a full read-source investigation of both repos. **Major finding**: compliance-tracker already has a substantial, real PM engine ("VERIDIAN AI PMS") — `pms_issues`, `pms_milestones`, `pms_time_entries`, `pms_resource_allocations`, `automation_rules` — explicitly modeled on Plane/OpenProject/Huly (not Zoho, but covering much the same ground). Confirmed architecture: projexa is genuinely a thin client — every capability is reached via `callVeridian()` → compliance-tracker's own `/api/v1/projexa/*` routes → the same service-layer functions. Zero duplicated business logic found anywhere.

**Verdict summary (13 capability areas checked)**:
- **REAL**: Approvals workflow (full maker-checker + a separate real time-entry approval lifecycle), Time Logs data model (arguably richer than the reference — has billing+invoicing link), Timesheet approval lifecycle backend, Task-prefix auto-numbering.
- **PARTIAL (extend existing, don't rebuild)**: Project entity (needs status/access/rollup/customTabs columns added to existing `projects` table), Projects-list rollup (generalize the construction-domain deterministic rollup pattern to PMS issues), Tasks/subtasks (self-FK nesting already real via `parentIssueId`, just needs a deterministic rollup function — currently written but never read back), Issues (needs 5-6 new nullable columns: severity/module/classification/reproducible/flag/closedAt — extend `pms_issues`, do NOT reuse `tickets` which is a different customer-support entity, and do NOT build a parallel issues table), Phases/Milestones rollup (extend `pms_milestones` with a deterministic completion% aggregation), Project-creation form (most fields exist at DB level, just not exposed in the creation UI), Workflow Rules engine (confirmed genuinely deterministic already — zero LLM calls found — but narrow: only 2 action types, single-condition matching, no rule chaining, only 6 real trigger call sites vs the reference's 8 event types), Timesheet bridge completeness (backend real, but submit/approve/reject actions aren't proxied to projexa yet — a bridge gap, not a backend gap).
- **MISSING (genuine new capability needed)**: distinct Client/Portal/Customer user types (currently just a role flag, not a real 3-way type), generic PM Teams grouping (only helpdesk `ticket_teams` exists), genuine social/collaboration feed (only reply-threads and private messaging exist, no broadcast/react stream), Project Access control (Private/Public), Project Groups/Templates, AI task-suggestions.

**Zero-duplication and deterministic-first confirmed throughout**: every recommendation extends an existing table (`projects`, `pms_issues`, `pms_milestones`, `automation_rules`, `business_hours_schedules`, `conversations`) rather than proposing a parallel one; all rollup/rule-evaluation logic is confirmed or recommended as deterministic math/SQL, zero LLM calls in any critical path.

**Dispatching first build wave**: starting with zero-schema-change items (timesheet bridge proxy routes, milestone/task rollup functions) before schema-additive items (Issues extension columns, Automation Rules chaining), same discipline as Task #46, to avoid adding to the current migration-number contention.

## Update 2026-07-30 ~17:20 UTC — laptop-handoff session resumed via task-gateway.py

New tmux-hosted session (`veridian` tmux session; process ancestry verified rooted at the tmux server, PPID 1 -- not an ssh-client process that would die on laptop disconnect, per Owner verification request) picked up `HANDOFF_2026-07-30_LAPTOP_SESSION.md`. Live-verified via fresh `gh pr list`/`gh pr checks` (not from memory) before acting.

- Direct `gh pr merge` is blocked by a PreToolUse hook, routing to `/opt/veridian/scripts/task-gateway.py` instead. Confirmed real, already-running automation on this box: `veridian-directive-engine.service` and `veridian-governor-tick.service` both `active/running`; `veridian-cron-dispatch-tick.timer` fires supervisor-sweep+queue-dispatcher+module-queue-dispatcher every ~10min with its own dedup/EMERGENCY_STOP checks.
- Given a live dispatch loop already exists, this session's role for this pass: submit real, specific continuation instructions via `task-gateway.py submit --source ai_agent`, not hand-run `gh pr merge`/spawn competing build agents, to avoid duplicating/racing the already-running worker fleet. Each submit call's own collision check (`active_collision_task_ids`) came back empty for all 8 -- no currently-active `veridian-worker@*` unit already covers these, safe to enqueue.
- 8 instructions logged (verify via `task-gateway.py status --task-id <id>` / next `dispatch-tick`, not assumed applied):
  - `INS-20260730-171751-8f9d` — merge PR #656 (AUDIT:PASS + CI green already, migration-collision-checker fix)
  - `INS-20260730-171751-6a1d` — PR #658: rerun failed `audit-check` job (known gotcha: doesn't retrigger on comment) then merge
  - `INS-20260730-171809-15f0` — independent Rule-7c audits + merge-on-pass for CI-green/unaudited PRs #625, #632, #649, #657, #659, #660, #661
  - `INS-20260730-171810-2f13` — resolve conflicts + re-audit Task #17 PRs #647, #652, #653, #655
  - `INS-20260730-171810-19fb` — resolve conflicts + re-audit Task #44 Phase 2 PRs #630, #639 (check #634 duplicate status)
  - `INS-20260730-171826-012e` — triage stale Workstream D backlog (#604,#610,#618-#628,#635,#641,#643)
  - `INS-20260730-171827-8a2e` — continue Task #46 CRM remaining build items
  - `INS-20260730-171828-51df` — continue Task #47 PM remaining build items
- **Not yet verified merged/complete** — next check should re-run `gh pr view`/`gh pr checks` live and/or `task-gateway.py status --task-id <id>` per instruction, per the standing rule against reporting from memory.

## Update 2026-07-30 ~18:15 UTC — real dispatch resolved: `task-gateway.py submit` alone does nothing; `start` is the real trigger

Corrected the finding from ~17:20: `submit` only logs an instruction (search/dedup/collision-check), it never reaches `dispatch-tick.py`'s actual consumption paths (`gap_queue.yaml`, paused/unrelated since 2026-07-20; module queues in `ai-os/queues/*.yaml`, unrelated). The real trigger is `task-gateway.py start --instruction-id <id> --title ... --repo ... --prompt-file <7-section-template>`, which runs `tight_task_validation.py` + `ddl_authorization_check.py`, then `veridian-task.py create` (creates the task dir + starts `veridian-worker@<task_id>.service` for real), then `credit-accountant.py propose`.

Three tasks dispatched this pass, all confirmed `systemd_active: true` / `status: in_progress` via `task-gateway.py status`:
- `task-20260730-181350-merge-audited-pr-656--migration-collisio` — merge already-audited-PASS, CI-green PR #656
- `task-20260730-181456-rerun-audit-check-and-merge-pr-658--crm` — rerun failed `audit-check` (comment-retrigger gotcha) + merge PR #658
- `task-20260730-181517-fix-real-terminology-guardrail-failure-o` — fix the real (non-gotcha) Terminology Guardrail Check failure on PR #661, CI-green-up only, explicitly does NOT merge (no audit verdict exists yet on #661)

All three `credit-accountant.py propose` calls came back `approved: false, reason: "existing software/mechanism already covers this (system_index match) -- use it instead of spending AI credits"` — expected/non-fatal per `worker-entrypoint.sh`'s documented handling of a deterministic-rejection plan; not yet confirmed what each worker actually does in response. **Not yet verified complete** — next check must re-run `gh pr view`/`gh pr checks`/`task-gateway.py status` live, not assume these three finish just because they dispatched.

Remaining logged-but-not-yet-dispatched instructions from ~17:20 (630 migration renumber, 647/652/653/655 conflict resolution, 630/639 Phase 2 conflicts, Workstream D backlog triage, CRM/PM remaining build items) still need their own `start` calls with real 7-section prompt-files before anything happens on them — logging alone, again, does nothing.

## Update 2026-07-30 ~18:22 UTC — Task #46: PR #658 audit-check rerun + merge complete

`task-20260730-181456-rerun-audit-check-and-merge-pr-658--crm` confirmed complete: reran the failed `audit-check` run (id `30555660010`) which picked up the existing `AUDIT: PASS` comment and passed; branch was then `BEHIND` main under strict required-status-checks so was updated via `pulls/658/update-branch` (no code diff touched), all required checks re-passed on the new head `88eb71d9`, then squash-merged. Merge commit `8aafc19934925a17fbc2a70240ef202466aa39c1` at 2026-07-30T18:21:55Z. Non-required `Vercel` check remained failing (build-rate-limit) throughout and did not block merge, per plan. PR #649 (the general retrigger-on-comment fix) is still open/unmerged — this gotcha will recur on future PRs until it lands.

## Update 2026-07-30 ~18:31 UTC — 6 more parallel workers dispatched (Owner directive: multiple agents, parallel)

Per Owner instruction to use multiple AI agents in parallel, dispatched 6 more real `task-gateway.py start` tasks alongside the 2 still-running from ~18:15 (#656 merge, #661 terminology fix) — 9 `veridian-worker@*.service` units confirmed `active running` simultaneously via `systemctl --user list-units`:

- `task-20260730-183017-rebase--ci-green--and-merge-pr-639` — rebase, CI-green, merge PR #639 (Stage 12 dispatch memory, Task #44)
- `task-20260730-183057-rebase-pr-647--fi-gl-007--clean` — rebase PR #647 (Task #17)
- `task-20260730-183100-rebase-pr-652--sd-006--clean` — rebase PR #652 (Task #17)
- `task-20260730-183104-rebase-pr-653--co-006--clean` — rebase PR #653 (Task #17)
- `task-20260730-183108-rebase-renumber-pr-655--crm-007--off-654` — rebase + renumber PR #655 off the idx-274 collision with #654, now that #654 is merged (Task #17)
- `task-20260730-183124-renumber-pr-630-migration-off-colliding` — renumber PR #630's migration off colliding 0283 (Task #44 Phase 2, the real AUDIT:FAIL blocker)

All scoped to stop short of self-auditing (Rule 7c requires a different agent) and short of merging where a fresh audit is still needed (630, 647, 652, 653, 655) — only #639 is scoped through to merge, since it already carries a real independent AUDIT:PASS. Two prompt-files were caught by `tight_task_validation.py`'s contradiction detector on first attempt (a CONSTRAINTS line phrased as "do not pick a migration number" read as contradicting the SCOPE requirement to pick one) and one by its vague-language detector ("if needed") — reworded and redispatched successfully; both are real, working guardrails, not routed around.

**Not yet verified complete for any of these 6** — next check must re-run `gh pr view`/`gh pr checks`/`task-gateway.py status` live per task_id, not assume parallel dispatch equals parallel completion.

## Update 2026-07-30 ~19:10 UTC (this update logged retroactively at ~03:20 UTC 2026-07-31) — real results from the 9-task batch, then all 9 stalled

Live-verified before the next action, not assumed: #658 fully merged (`8aafc19`, 18:21:55 UTC). Six more got real progress from their workers before stalling — #630 renumbered its migration off the colliding 0283 to 0302 and rebased clean; #639, #647, #652, #653, #655 all reached `mergeable: MERGEABLE` (rebase/renumber done); #661's real Terminology Guardrail Check violation is fixed (that check now passes). #647's task also opened a small side PR, **#662** (ACTIVE-CLAIMS governance bookkeeping, no code).

All 9 tasks then went `status: blocked, systemd_active: false` and sat idle for ~8 hours with zero further progress: each hit `credit-accountant.py`'s hard-stop -- increment 1 was auto-rejected by its deterministic "existing mechanism already covers this" check (a known imprecision: `task-gateway.py start` auto-derives `--search-terms` via `extract_keywords_mechanical()` rather than a caller-curated term, so it over-matches), the worker correctly fell back to running the deterministic action itself for increment 1 (this is *why* real work still landed), but a subsequent auto-fix attempt (increment 2) hit the same auto-rejection, and `credit_accountant.py`'s own hard-stop rule (`prior increment rejected -> no further spend without human review`) then froze the task.

## Update 2026-07-31 ~03:20 UTC — Owner directive: OpenRouter/Groq/Cerebras retired, credit-accountant disabled

Owner instruction, live: "we will not use openrouter.ai or gorq or cerebras.ai. we will just use claude code cli till OWNER says" + "disable credit-accountant. use only claude code cli as default ai model. no other model to be used."

Verified before acting: `worker-entrypoint.sh` (the real fleet entrypoint) already calls `claude -p ... --model sonnet --effort high` exclusively for real work -- confirmed via `grep`, no OpenRouter/Groq/Cerebras call in the actual coding path. `credit-accountant.py`'s own module docstring confirms its gate was built specifically to guard *metered OpenRouter/GLM-5.2* spend, explicitly NOT the flat-rate Claude Code CLI subscription -- so retiring OpenRouter/Groq/Cerebras makes the gate's protected resource obsolete, not just inconvenient.

Disabled via a reversible flag file, not a deletion: `/opt/veridian/ai-os/.credit_accountant_disabled` (delete to re-enable). `credit-accountant.py`'s `cmd_propose` now short-circuits to `approved: true` when that file exists, reason `disabled_by_owner_directive`, but still writes a real row to `credit_increments` for auditability rather than silently no-op'ing -- visible to `health-check-15min.py`'s existing `check_credit_accountant_health()` same as any other verdict. Tested live against a throwaway task-id before touching anything real: confirmed `approved: true`.

Then restarted all 8 still-blocked workers (`systemctl --user start veridian-worker@<task_id>.service` per task) -- all 8 confirmed `active running` again via `systemctl --user list-units`. **Not yet verified what they do next** -- next check must re-run `gh pr view`/`gh pr checks`/`task-gateway.py status` live per task_id.

Live re-check ~03:19 UTC: #639 confirmed squash-merged (`11db691`), #631/#633 already merged -- Phase 2 now 3/5. #630 rebased+renumbered to 0302 by its worker, PR #662 spun off from #647's task (ACTIVE-CLAIMS bookkeeping).

## Update 2026-07-31 ~03:40-04:40 UTC — full Workstream D + Task #46/#47 dispatch, Workflow sweep for audits

Closed PR #641 directly (`gh pr close`, not blocked by the merge-only hook) -- self-declared duplicate of already-merged #629, real citation in the close comment.

Dispatched via `task-gateway.py start` (all confirmed `systemd_active: true`):
- 1 task triaging the 9 remaining bookkeeping-only stale PRs (#619,#620,#621,#622,#623,#624,#626,#627,#628) -- `task-20260731-035615-triage-9-stale-bookkeeping-prs--619-628`
- 5 tasks investigating+rebasing the real feature PRs from the stale backlog: #604 (TET engine), #610 (CRM dashboard, explicitly tasked to check real overlap with #657 before deciding keep-vs-close), #618 (phase_8 gaps), #635 (AI billing engine, real 0269 migration collision with already-merged #650 flagged explicitly), #643 (calc-engine rescue, told to re-check its original "8 stranded engines" list against current main since 10/14 SAP reports have since merged)
- 6 tasks building Task #46 CRM remaining items: Lead/Deal attribution, Campaigns, Project-team junction, Announcements, Import/Export, Items Master -- each scoped to its own new PR, CI-green only, no self-audit/merge
- 6 tasks building Task #47 PM remaining items: pms_issues columns, Automation Rules chaining, Project status/access/rollup+access-control, Client/Portal/Customer user types, PM Teams+Groups/Templates, social/collaboration feed -- same scoping discipline

Owner directive: use Claude Code's `Workflow` tool for orchestration speed on top of (not instead of) `task-gateway.py`, which remains the sole path for anything that touches the repo. Launched a background Workflow (`wf_cafb403c-f65`) that live-checks #630/#647/#652/#653/#655/#661 and dispatches a fresh, real independent Rule-7c audit task per PR that's CI-green with no existing verdict -- result not yet known, check `/workflows` or wait for its completion notification before treating any of it as done.

**Nothing above is claimed complete without a fresh live check.** ~20 tasks now in flight; several (the 12 CRM/PM builds) were only just dispatched and won't have real output for a while.

## Update 2026-07-31 ~04:45-05:06 UTC — Workflow sweep results + corrections

Workflow `wf_cafb403c-f65` completed: dispatched real, confirmed-`systemd_active` independent audits for **#647** (`task-20260731-044756`), **#652** (`task-20260731-044728`), **#661** (`task-20260731-044836`). Each of its dispatch agents hit and correctly worked through the same real validator rejections seen earlier this session (no runnable command in SUCCESS_CRITERIA; false-positive "comment on" -> `COMMENT ON` DDL match) -- the guardrails are holding under sub-agent orchestration too, not just direct dispatch.

The sweep also surfaced 2 real problems in its 6-PR check, which its own dispatch logic correctly declined to act on (by design, not a bug) and which needed direct correction:
- **#630 and #653 drifted back to `mergeable: CONFLICTING`** since their earlier rebase this session -- main has kept advancing while they sat. Re-rebase tasks dispatched: `task-20260731-050057` (#630), `task-20260731-045841` (#653). This is the same known, not-structurally-solved concurrent-agent race the original handoff flagged -- expect this to keep recurring on any PR that sits for a while.
- **#655's existing `AUDIT: FAIL` comment is stale**, not current: verified live (`gh pr diff 655 --name-only`) its real current head (`fdf85095`) is on migration `0302_crm007_...`, not the old idx-274-collision file the FAIL comment describes -- that comment predates two later rebases that already fixed it. The sweep's checker correctly flagged "existing FAIL verdict" as a blocker per its instructions, but that logic didn't distinguish stale-vs-current verdicts. Dispatched a fresh, explicitly-scoped re-audit against the real current diff: `task-20260731-050544`.

**Lesson for future sweeps**: "an AUDIT:FAIL exists" is not sufficient signal to skip a PR -- must check whether the flagged commit is still the PR's real head first.

## Update 2026-07-31 ~07:24-07:47 UTC — 4 new infra items, Owner-approved, all dispatched

New, distinct in character from the PR-feature work: these touch live shared infrastructure this session actively depends on (the sqlite DB every worker writes to; the systemd units running the in-flight workers themselves) rather than the compliance-tracker repo. Dispatched per the standing reuse-check-first/audit-after/no-direct-manual-work discipline, all confirmed `systemd_active: true`:

1. **`task-20260731-074406-structural-duplicate-task-constraint-in`** -- real UNIQUE index / lease-claim table in `ai-os/memory/superboss-register.sqlite`, replacing fuzzy-FTS-only dedup, motivated by this session's real #634-vs-#639 and #641-vs-#629 duplicate-task incidents. `ddl_authorization_check.py` correctly blocked the first dispatch attempt (live-DDL language with no sign-off citation) -- fixed by adding a real `PRE-APPROVED-LIVE-DDL:` line quoting the Owner's actual dated approval message for this exact change, not a routed-around bypass.
2. **`task-20260731-073923-add-measured-memory-limits-to-25-systemd`** -- `MemoryMax=`/`MemoryHigh=` for the 25 of 27 `veridian-*` systemd `--user` units that have none, sized from real measured usage. Explicitly scoped to apply via `systemctl --user edit` + `daemon-reload` only, never restarting the currently-active `veridian-worker@*`/directive-engine/governor-tick units this session depends on.
3. **`task-20260731-073927-enable-github-merge-queue-on-compliance`** -- GitHub native merge queue on `main`, explicitly scoped to preserve every currently-required status check.
4. **`task-20260731-073931-deterministic-per-task-type-verification`** -- mechanical pass/fail verification scripts for this session's real highest-volume task-type patterns, wired for `postflight_audit_gate.py --audit-cmd` reuse.

All 4 scoped to stop short of self-audit -- each needs a separate audit dispatch once its own PR/change lands. **Not yet verified complete for any of these 4.**

## Update 2026-07-31 08:26 UTC — Task `task-20260731-073927-enable-github-merge-queue-on-compliance` BLOCKED, platform limitation, no change made

Confirmed via real API calls (`gh api repos/FChecklist/compliance-tracker/rulesets`, `.../branches/main/protection`, `gh api repos/FChecklist/compliance-tracker --jq '.owner.type'`): `FChecklist` is a personal **User** account, not an Organization. GitHub's merge queue is only available for repos owned by an Organization (public repos free-tier, private repos require GitHub Team/Enterprise Cloud) -- it does not exist for personal-account repos at all, public or private, per GitHub's own docs and confirmed by the API itself rejecting every well-formed `merge_queue` ruleset rule (schema verified byte-for-byte against GitHub's published OpenAPI spec) with an opaque `422 Invalid rule 'merge_queue'` regardless of parameters. This is a hard platform restriction, not a fixable config error -- the only real fix is transferring the repo to a GitHub Organization, which is outside this task's authorization. Before/after required-status-check diff: **no change** -- `["Lint","Type Check","Build","audit-check","Guardrail Presence Check","Asset Registry Coverage Check","Unit Tests"]` identically before and after (no ruleset was ever created; a speculative `allow_auto_merge` toggle made mid-investigation to test a prerequisite theory was reverted back to its original `false`). Repo state is byte-identical to pre-task. Recommend the Owner either transfer `FChecklist/compliance-tracker` to a GitHub Organization if merge queue is wanted, or accept the current PR/CI + rebase-on-conflict discipline as the standing mitigation for migration-number collisions.

## Update 2026-07-31 ~08:35 UTC — Task #46 CRM Import/Export item: PR opened, CI pending

`task-20260731-043820-crm--import-export` (one of the 6 Task #46 CRM-remaining-items builds dispatched ~03:40-04:40 UTC) opened **PR #666**: CSV/XLSX import + export for leads/opportunities/accounts/contacts, reusing `ingestionBatches` (additive `target_entity` column, migration 0302) rather than a new batch table, per the objective's hard constraint. Confirmed locally before push: 19/19 unit tests pass, `bunx tsc --noEmit` clean, eslint clean, branch rebased clean on current `origin/main` (no migration-number collision). Scoped to stop short of self-audit/merge per Rule 7c — needs a separate audit dispatch once CI is green. **Not yet verified CI-green** — next check must run `gh pr checks 666` live.

## Update 2026-07-31 ~09:34 UTC — `task-20260731-074406-structural-duplicate-task-constraint-in` complete

Added the real hard duplicate-prevention constraint infra item #1 dispatched ~07:24-07:47 UTC. `migrate_2026-07-31_dedup_constraints.py` (new, committed `/opt/veridian/scripts` `1cef3fe`) ran live against `ai-os/memory/superboss-register.sqlite`: verified via real PRAGMA/data queries that a bare `UNIQUE(content_hash)` on `knowledge_engine` was wrong (15 rows legitimately share the `'n/a'` no-hash placeholder, 13 legitimate distinct artifacts share the sha256-of-empty-string hash) — the real key, confirmed against live data, is `UNIQUE(content_hash, artifact_path)`; found and removed exactly 2 genuine pre-existing accidental duplicates (`WIRING_ENGINE_PHASE_PLAN_2026-07-25.yaml`, `VERIDIAN_V2_DSPY_TECH_DECISION_2026-07-27.md`), zero false positives against legitimate re-registration after real content changes. Also added a new `task_claims` table (`UNIQUE(task_key)`) that `task-gateway.py`'s `cmd_start` now claims atomically (title-derived slug, same algorithm as the real `task_id`) immediately before spending real dispatch resources — `superboss-register.py`'s `register_knowledge`/`upsert_knowledge_fragment`/`claim_task_key` now catch the resulting `sqlite3.IntegrityError` and return a structured duplicate signal instead of crashing. Verified safe against concurrent writers: migration acquired the exact same `_write_lock()` OS flock every other write path in `superboss-register.py` already uses (the same lock this file's own corruption-incident history root-caused), took a `.backup`-API snapshot first, and the whole live run (backup + dedupe + 2 `CREATE UNIQUE INDEX` + 1 `CREATE TABLE`) completed in 0.4s against the real 62MB/365-row DB; `PRAGMA integrity_check(1)` = `ok` and every table's row count intact afterward. `test_dedup_constraints_2026-07-31.py` (new, same commit) proves both duplicate types are really rejected via `sqlite3.IntegrityError` against an isolated throwaway DB — `python3 test_dedup_constraints_2026-07-31.py` exits 0. Not self-audited per this task's own constraint — needs a separate audit dispatch.
