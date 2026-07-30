# UTM Metadata Consolidation -- Phase 6 (2026-07-30)

campaign: utm-metadata-consolidation-phase6-2026-07-30
purpose: Owner directive -- evaluate whether every other real metadata mechanism
in VERIDIAN can genuinely merge into the UTM standard (utm_source/utm_medium/
utm_campaign/utm_content/utm_term), without forcing substantive business/
technical data into 5 generic string fields where that would lose type
safety, queryability, or break real logic. Written so a future AI/software
session can read the real current metadata architecture without
re-investigating from scratch.

UTM's own canonical semantics (from superboss-register.py's own header,
verified 2026-07-30, unchanged from prior sessions):
- utm_source: who (owner|end_user|org|ai_agent|software)
- utm_medium: channel (ssh_session|claude_code_cli|chat_ui|api|cron)
- utm_campaign: initiative/project grouping, freeform slug
- utm_content: short structured label of what (not a sentence)
- utm_term: comma-separated search keywords

Tables already carrying real UTM columns as of today (verified via live
PRAGMA table_info, not memory): `instructions`, `work_items`, `actions`,
`system_index`, `capability_registry` (added Stage 7 pilot, 2026-07-29,
11 rows -- was live but NOT yet committed to the claude-control repo until
this phase's PR #117 also reconciled that drift), `umr_tasks` (added
2026-07-29, 104 rows -- its UTM columns are currently a direct 1:1 mirror of
pre-existing substantive columns: utm_source='owner_engine',
utm_medium='submit', utm_campaign=source_trigger, utm_content=task_kind,
utm_term=task_identity -- i.e. umr_tasks' own UTM adoption is itself just a
convention-alignment layer over real columns that already existed, not new
information; nothing further needed there this phase).

## 1. capability_registry's own fields (superboss-register.sqlite)

Real schema (verified live): capability_id, ts, capability_name, inputs,
business_rules, workflow, automation, documents, reports, apis, ui_screens,
permissions, ai_required, confidence, version, owner, last_verified_ts,
metadata_json, utm_source, utm_medium, utm_campaign, utm_content, utm_term.

**Determination: SUBSTANTIVE-DATA (already correctly using UTM for its
intended purpose; nothing further to merge).** version/confidence/
ai_required/business_rules/workflow/automation/documents/reports/apis/
ui_screens/permissions are real structured JSON/typed data describing a
capability's actual behavior -- forcing e.g. `confidence` (a REAL used in
real threshold comparisons) or `business_rules` (structured JSON, not a
string) into a utm_* field would lose type safety for zero benefit. UTM here
is already deployed exactly as intended: a provenance/registration envelope
(utm_source=registering script, utm_medium=subcommand, utm_campaign=
classification group, utm_content=file/locator, utm_term=capability name),
layered ON TOP of the real substantive fields, not replacing them. This is
the reference pattern the other 5 mechanisms below were each judged against.

## 2. wiring_registry's own fields (superboss-register.sqlite)

Real schema (verified live -- corrects the task brief's assumed field list
of "path, purpose, calls, called_by", which does not match current reality):
entity_id, ts, entity_type, source_system, path, relationships,
last_verified_ts, verification_status, source_ref, metadata_json,
content_hash. No `purpose`, `calls`, or `called_by` columns exist -- calls/
called_by-style data lives inside the `relationships` JSON structure instead.
7,795 live rows. entity_type has 8+ distinct real values (file, engine,
ai_role, browser_component, cron_job, dispatch_event, function, gateway,
...). source_system has exactly 4 distinct real values: github, server,
supabase, vercel -- the same 4 systems PROTOCOL_OWNER_AI.yaml's own §9
"SYSTEM definition" names (Server + Supabase + Vercel + GitHub).

**Determination: SUBSTANTIVE-DATA, correctly kept separate -- NOT merged.**
Reasoning: source_system LOOKS superficially UTM-source-shaped (small
controlled vocabulary indicating origin), but (a) it does not match UTM's
own defined utm_source vocabulary (who: owner|end_user|org|ai_agent|
software) -- source_system answers WHICH of the 4 platforms, a materially
different dimension, so mapping it to utm_source would be a real semantic
conflation, not a clean merge; (b) it is not a duplicate/second mechanism
tracking anything UTM already tracks for this table (wiring_registry never
had UTM columns before today) -- there is nothing to deduplicate; (c) it is
a heavily-used, real first-class query dimension (generate_wiring_registry.py,
dispatch_core.py, and multiple audits filter/join on entity_type and
source_system by name) across 7,795 rows -- renaming/merging would be pure
churn with real regression risk across many call sites for zero
simplification gain, which fails the Owner's own "don't force it if it would
break real functionality" guardrail. content_hash/verification_status/
relationships are real audit/structural data (hash values, CHECK-constrained
enum, dependency-graph JSON) -- same category as capability_registry's own
fields above.

Cross-boundary vocabulary note (per the Owner's item 3 guidance -- align
vocabulary rather than force a literal merge): any NEW table that tags
records with "which of the 4 systems" going forward should reuse
wiring_registry's existing {github, server, supabase, vercel} vocabulary for
that dimension (whether as its own source_system-style column or, only if
that specific dimension is really what's meant, as utm_source values), rather
than inventing a 5th naming scheme. No code change needed here today --
documented for future consistency only.

## 3. prompt_versions (compliance-tracker Postgres, Wave 22 Prompt OS)

Real schema (verified live via schema.ts, complianceSchemaDB.table
'prompt_versions'): id, promptTemplateId, version, content, label
('production'|'staging'|null, service-layer-enforced: only one version per
template may hold a given label at a time), isActive (boolean), createdById
(nullable), createdAt.

**Determination: SUBSTANTIVE-DATA. Correctly kept separate.** label and
isActive are real, actively-enforced serving-state that directly gates WHICH
prompt content is live in production right now -- this is exactly the
Owner's own named example of what NOT to force into a generic tag (a
capability/record's classification/status driving real logic). Squashing
label/isActive into a utm_* string would (a) lose the service-layer's
uniqueness enforcement (a real invariant: only one 'production'-labeled
version per template), (b) make "what's actually live" unqueryable without
string-parsing. createdById is a real (soft) FK to a user, not a category.

## 4. orchestraExecutions / activityLog (compliance-tracker Postgres)

Real schema (verified live): orchestraExecutions has eventType, input/output
(jsonb), status, durationMs, model, provider, promptTokens, completionTokens,
costUsd, routingRationale, payloadPurgedAt. activityLog has activityType,
detailTable/detailId, lifecycleStage (requested|classified|validated|
executed...), objective, selfAssessment (jsonb), reviewedBy, reviewNotes,
reviewDecision (approved|rejected), riskLevel, confidencePercentage,
confidenceBand, complexityTier.

**Determination: SUBSTANTIVE-DATA. Correctly kept separate.** This is the
Owner's other explicitly-named example (a resource-metric value) made
concrete: promptTokens/completionTokens/costUsd are real numeric metrics
that get SUM()'d/aggregated in cost dashboards (model-scorecard-service.ts,
token-usage/route.ts) -- stuffing a numeric cost into a utm_* TEXT field
would break real aggregation queries and is exactly the anti-pattern the
Owner pre-empted. status/lifecycleStage/reviewDecision/riskLevel/
confidenceBand are real state-machine values gating real control flow
(review-required routing, tier-eligibility checks) -- not descriptive tags.

## 5. task_capabilities (compliance-tracker Postgres)

Real schema (verified live, platformSchemaDB.table 'task_capabilities'):
capabilityKey (unique), modePill, pathKeys (jsonb), status ('ai_only'|
'partial'|'full_software'), needsImprovement, version (bumped only on real
implementation change), lastAuditedAt/lastAuditedVersion, occurrenceCount,
promptWordIndex (jsonb), fullSoftwareCount/packageAvailableCount/novelCount,
orgId, timestamps.

**Determination: SUBSTANTIVE-DATA. Correctly kept separate.** status is
literally the Owner's own named example ("a capability's classification
status") of data that must NOT be forced into a tag -- it's a real 3-value
enum read by ai-reduction-service.ts to compute whether AI-dependence is
decreasing over time. version/lastAuditedVersion gate the Auditor's real
"once per version" dedup logic. occurrenceCount/fullSoftwareCount/
packageAvailableCount/novelCount are real cumulative counters aggregated
into monthly snapshots (aiReductionSnapshots) -- same numeric-metric
argument as orchestraExecutions above.

## 6. knowledge_engine's own fields (superboss-register.sqlite) -- THE ONE GENUINE MERGE

Real schema before this phase (verified live): artifact_id, ts,
artifact_path, content_hash, artifact_type ('canonical'|'derived'),
secondary_path, exists_on_disk, purpose, tags, entity_relationships,
last_verified_ts, verification_status, metadata_json. 350 live rows.

`tags` is a JSON array of free-form keyword strings with an informal,
already-established convention: plain category words ("governance",
"canonical", "audit", "architecture", ...), plus prefixed pairs
("source:SERVER", "source:VERCEL", "registry:constitution", ...). 618
distinct tag tokens across 350 rows -- including at least one real data-
quality bug found in passing (one row's "tags" array contains a full
sentence, "2026-07-26. 4/4 real gates found and registered", where a
progress note was clearly appended as a tag by mistake instead of into
metadata_json.corrections; left as-is, not fixed, since fixing arbitrary
historical data-entry mistakes was out of this phase's scope and risks
misreading intent -- flagged here for whoever next touches that row).

**Determination: GENUINE-UTM-CANDIDATE -- merged this phase.** `tags` is
purely descriptive/categorical, not driving any control-flow logic (grep of
the full 167KB superboss-register.py + adjacent audit scripts found only
read/search usage of `tags`, e.g. query_knowledge()'s `--tag` filter and the
FTS5 index -- never a decision branch keyed on tag content). Critically,
this file's OWN header docstring already defines utm_term as "comma-
separated search keywords" -- which is *exactly* what tags already is,
just JSON-array-shaped instead of comma-string-shaped. This is a real,
lossless, format-only duplication of a mechanism the system already has a
name and column for, not a second mechanism carrying distinct information.

**What was NOT merged, and why:** `purpose` (a real one-line prose
description sourced from the artifact's own header, not a short categorical
label -- utm_content is explicitly defined as "not a sentence"; forcing
purpose in would violate that shape and is unnecessary since purpose already
has its own column) and artifact_type/verification_status/content_hash/
entity_relationships (CHECK-constrained enums, a real hash, and a real
JSON relationship graph -- all structural/audit data, same category as
capability_registry's/wiring_registry's own fields above) all correctly
stay OUT of UTM.

### Real implementation (verified live, not just planned)

1. Backed up superboss-register.sqlite (rename-copy,
   `superboss-register.sqlite.pre-utm-knowledge-engine-merge-20260730-035949Z.bak`)
   before any schema change, per safe-edit discipline.
2. Added utm_source/utm_medium/utm_campaign/utm_content/utm_term (all
   nullable TEXT) to the live knowledge_engine table via ALTER TABLE ADD
   COLUMN (SQLite-safe, non-rewriting, non-breaking to existing readers).
3. Backfilled utm_term = comma-join(tags) for all 350 existing rows.
   Verified: row count unchanged (350 before/after -- no data loss/
   duplication), 0 rows left with NULL utm_term after backfill.
4. Added `_migrate_knowledge_engine_utm()` to superboss-register.py, mirroring
   the exact existing `_migrate_capability_registry_utm()` pattern (same
   idempotent ALTER-then-backfill convention already used for the Stage 7
   capability_registry UTM pilot) -- called from `_ensure_knowledge_engine_table`.
   Verified idempotent: re-running via `list-knowledge` against the
   already-migrated live DB is a clean no-op (0 additional rows touched).
5. `register_knowledge()` now auto-derives utm_term from --tags on every
   future insert (never asked for twice), and accepts optional
   --utm-source/--utm-medium/--utm-campaign/--utm-content, matching
   log-instruction's existing --source/--medium/--campaign/--content/--term
   interface convention. Historical rows' utm_source/utm_medium/utm_campaign/
   utm_content are honestly left NULL (no reliable per-row "who registered
   this" data exists retroactively for knowledge_engine, unlike
   capability_registry's owner-field-based backfill) -- not fabricated.
6. `tags` and `knowledge_engine_fts` (which indexes tags, not utm_term) were
   deliberately left untouched -- still the real FTS5 search surface and the
   shared --tags convention with `index-add`; nothing that reads tags today
   breaks.
7. Real drift also found and reconciled while doing this: the live deployed
   `/opt/veridian/scripts/superboss-register.py` had already diverged from
   the claude-control repo's master branch (the Stage 7 capability_registry
   UTM pilot was live but never committed -- likely because the normal
   git-pull/deploy-live-scripts.sh auto-sync cron is still stopped per the
   2026-07-26 OOM-incident pause). Both that pilot's code AND this phase's
   knowledge_engine change were committed together in
   github.com/FChecklist/claude-control PR #117, merged (verified via
   `gh pr view --json state,mergedAt` -> MERGED), then `deploy-live-scripts.sh`
   was re-run and confirmed byte-identical (sha256
   4844152d6bc9d265d3f19609f36f576bfd9331cd570f8240c0cf35545772cb84) between
   the repo and the live file -- repo and live are back in sync.

## Correlation-ID wiring (umr_tasks.metadata_json.correlation_id)

Real current state, checked directly today (not repeated from memory):
exactly 1 of 104 live umr_tasks rows carries a correlation_id
(`UMR-20260729-183721-6bb0` -> `{"correlation_id": "CT-VERIFY-CORR-0001"}`) --
a single manually-set verification-test value, not written by any real
running code path.

Looked specifically for the bridge point named in this phase's brief (an
Owner-side dispatch script invoked FROM a Vercel API route via SSH/webhook),
beyond what the earlier pass checked:
- Grepped every compliance-tracker `src/app/api` route for
  `resource_governor`, `task-gateway`, `veridian-task.py`, `OWNER_ENGINE`,
  the server's IP, and any `child_process`/`exec`/`spawn` usage: zero
  matches anywhere in the API tree.
- Read `/api/ai/team/dispatch/route.ts` (the one real end-user-triggerable
  AI dispatch endpoint, POST /api/ai/team/dispatch) directly: it classifies
  a task to an AI Workforce role and calls `runRole()` in-process against
  LLM providers directly (OpenRouter/etc) -- it never shells out, never
  touches SSH, never references the Hetzner server. Confirmed via its own
  source, not inferred.
- Checked `.github/workflows` in compliance-tracker for anything
  referencing the server/SSH: none exist.
- Checked `/opt/veridian/scripts` for any inbound HTTP listener (Flask/
  FastAPI/http.server) that a Vercel webhook could call into: none exist --
  every Owner-engine dispatch script (resource_governor.py, task-gateway.py,
  veridian-task.py) is CLI-invoked only, from an interactive SSH session.

**Conclusion, unchanged from the earlier pass but now checked from more
angles: no real, currently-existing code path lets an end-user action on
the compliance-tracker/Postgres side reach the Owner-engine's submit()
boundary.** The two systems are architecturally separate by current design:
the Vercel-hosted product's own "AI Team" (roster.ts/dispatch route) talks
to LLM providers directly and is a genuinely different subsystem from the
Hetzner server's internal dev-ops/autonomous-engineering task queue
(umr_tasks/resource_governor.py) that only this kind of interactive session
drives. Per the Owner's own instruction not to fabricate a bridge that
doesn't exist: no further correlation_id wiring was done this phase. If a
real bridge is ever built (e.g. a future webhook/queue connecting end-user
product events to Owner-engine dispatch), that would be the point to wire
metadata_json.correlation_id through for real -- until then this field
stays real-but-unused, honestly documented as such rather than silently
dropped or fabricated-as-wired.

## Summary table

| Mechanism | Verdict | Action |
|---|---|---|
| capability_registry own fields | SUBSTANTIVE (UTM already correctly layered on top) | none needed |
| wiring_registry own fields | SUBSTANTIVE, correctly separate | documented vocabulary-alignment note only |
| prompt_versions (Postgres) | SUBSTANTIVE, correctly separate | none |
| orchestraExecutions/activityLog (Postgres) | SUBSTANTIVE, correctly separate | none |
| task_capabilities (Postgres) | SUBSTANTIVE, correctly separate | none |
| knowledge_engine.tags | GENUINE-UTM-CANDIDATE | merged into utm_term (PR #117, merged + deployed live, verified) |
| umr_tasks.metadata_json.correlation_id | real field, not yet wired | no real bridge found this phase either; honestly left unwired |
