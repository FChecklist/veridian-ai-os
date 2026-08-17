# MANDATORY STOP CONDITION & ESCALATION RECORD

**Date:** 2026-08-17  
**Triggered by:** Step 1 (Existence Matrix) completion  
**Reference:** SPEC section "MANDATORY STOP CONDITIONS - escalate, never push through"

---

## Stop Condition Triggered

Per spec: "A gap needs a schema, an API contract, or a design decision."

**STATUS: ✅ CONFIRMED TRUE**

Of 28 protocol items (P0.1 through P7.2a), analysis found:

| Category | Count | Requirement |
|----------|-------|-------------|
| **Gaps needing schema** | 5 | P0.2 (fingerprint), P0.3 (UUID v7), P2.1 (registry), P7.1 (metrics), P6.2 (role field) |
| **Gaps needing design decision** | 6 | P0.1 (source enum), P0.3a (role priority), P3.3a (100% confidence), P3.1 (queue phases), P5.2 (model selection), P6.2 (role hierarchy) |
| **Gaps needing API contract** | 3 | P2.1 (fingerprint lookup), P4 (gap report schema), P4 (patch format) |
| **Gaps needing cross-repo contract** | 3 | P4 (AI model integration), P5 (lightweight model integration) |

**Result:** Zero gaps meet Step 2 criteria (all 5 conditions). Cannot proceed with implementation.

---

## Mandatory Escalations

All items below require **JUDGMENT-class work** per spec: "Do not implement. Register it as a child work item with the correct complexity, using integrative or judgment for anything involving schema design, cross-repo integration, or duplicate resolution."

### SET A: Schema Design (5 items)

#### ESC-1: P0.2 - SHA-256 Fingerprint Field
- **Scope:** Add `fingerprint: text` column to tasks table
- **Complexity:** INTEGRATIVE (must update all task creation/lookup code)
- **Blockers:** None
- **Depends On:** None
- **Effort:** 2-3 days
- **Affected Repos:** compliance-tracker
- **Notes:** SHA-256(tenant_id + role_level + MODE_PILL + OPTION_SELECTION + CHAT)

#### ESC-2: P0.3 - UUID v7 Migration
- **Scope:** Change tasks.id generation from createId() to UUID v7
- **Complexity:** JUDGMENT (backwards compatibility, migration strategy)
- **Blockers:** ESC-1 should be done first (coordination)
- **Depends On:** Database migration tool decision
- **Effort:** 3-5 days
- **Affected Repos:** compliance-tracker, projexa (client-side handling)
- **Notes:** May require database migration; impacts all task lookups

#### ESC-3: P2.1 - Fingerprint Registry Table
- **Scope:** Create fingerprint_registry table (fingerprint PK, tenant_id, version, data)
- **Complexity:** INTEGRATIVE (multiple services need to write/read from this)
- **Blockers:** ESC-1 must be complete (fingerprint format)
- **Depends On:** P2.1 API contract decision (see ESC-B2)
- **Effort:** 2-3 days
- **Affected Repos:** compliance-tracker
- **Notes:** Server-side global registry; must be scoped per tenant

#### ESC-4: P7.1 - Metrics Table
- **Scope:** Create execution_metrics table (tenant_id, metric_type, local_hit_count, global_hit_count, gap_fill_count, timestamp)
- **Complexity:** INTEGRATIVE (multiple services emit metrics)
- **Blockers:** None
- **Depends On:** Metric collection strategy decision (sampling vs all events)
- **Effort:** 1-2 days
- **Affected Repos:** compliance-tracker, ai-os/scripts
- **Notes:** Critical for P7.2a gate verification

#### ESC-5: P6.2 - Role Level Field
- **Scope:** Add `minimum_required_role_level: integer` to tasks table
- **Complexity:** JUDGMENT (requires role hierarchy definition)
- **Blockers:** Role hierarchy decision (ESC-D1)
- **Depends On:** ESC-D1
- **Effort:** 1-2 days
- **Affected Repos:** compliance-tracker
- **Notes:** Depends on role enum/hierarchy definition

### SET B: API Contracts (3 items)

#### ESC-B1: P2.1 - Fingerprint Lookup API
- **Scope:** POST /api/task/lookup-by-fingerprint { fingerprint, tenantId } -> { taskId, cached, version }
- **Complexity:** JUDGMENT (response format, caching headers, auth)
- **Blockers:** ESC-3 (registry table)
- **Depends On:** API design decision (REST vs GraphQL, auth strategy)
- **Effort:** 1-2 days
- **Affected Repos:** compliance-tracker (backend), projexa (client)
- **Notes:** Must support both cache-hit and cache-miss responses

#### ESC-B2: P4 - Gap Report Schema
- **Scope:** Define gap_report JSON schema (what constitutes a "gap"?)
- **Complexity:** JUDGMENT (architectural decision about gap types)
- **Blockers:** None
- **Depends On:** Definition of P3.3a "100% confidence" criteria
- **Effort:** 2-3 days (requires Owner input on gap taxonomy)
- **Affected Repos:** compliance-tracker, ai-os/scripts, external AI model
- **Notes:** Scope examples: missing_index? missing_rule? missing_validation? All of the above?

#### ESC-B3: P4 - Configuration Patch Format
- **Scope:** Define patch format (YAML/JSON/SQL) and integration mechanism
- **Complexity:** JUDGMENT (patch application strategy)
- **Blockers:** ESC-B2 (gap report schema)
- **Depends On:** Patch application framework decision
- **Effort:** 2-3 days
- **Affected Repos:** compliance-tracker, external rule engine
- **Notes:** Must define max 2 iteration enforcement and re-run orchestration

### SET C: Design Decisions (6 items)

#### ESC-D1: P0.1 - Input Source Type Enum
- **Scope:** Define enum values for input source: {human_typing, machine_sensor, api_call, ai_agent_request, link_click, ...others?}
- **Complexity:** JUDGMENT (product/business decision)
- **Blockers:** None
- **Depends On:** Product requirements from Owner
- **Effort:** 0.5-1 day
- **Affected Repos:** All (used in P0 ingestion)
- **Notes:** Will be stored as source_type: text in tasks table

#### ESC-D2: P0.3a - High-Priority Role Definition
- **Scope:** Define which roles are "high priority" for P0.3a gate (front-of-queue routing)
- **Complexity:** JUDGMENT (business/security decision)
- **Blockers:** ESC-D1 (source type), role hierarchy decision
- **Depends On:** Role hierarchy definition (ESC-D4)
- **Effort:** 0.5-1 day
- **Affected Repos:** compliance-tracker (queue router)
- **Notes:** Examples: admin? owner? C-level? Scope: PROJEXA construction site context

#### ESC-D3: P3.3a - "Exactly 100% Confidence" Criteria
- **Scope:** Define what "EXACTLY 100% ... evidenced by schema match + index used + historical success" means
- **Complexity:** JUDGMENT (architectural decision - can deterministic software ever be truly 100%?)
- **Blockers:** None
- **Depends On:** Existing system's current confidence thresholds (already uses 0.95)
- **Effort:** 1-2 days (may require Owner discussion on acceptable risk)
- **Affected Repos:** compliance-tracker (task-execution-engine, instruction-execution-cache-service)
- **Notes:** Current system uses 0.95; increasing to 1.0 may drastically reduce cache hits

#### ESC-D4: P6.2 + P0.3a - Role Hierarchy Definition
- **Scope:** Define complete role hierarchy (admin, owner, manager, user, guest, ...others? with priority levels)
- **Complexity:** JUDGMENT (organizational structure decision)
- **Blockers:** None
- **Depends On:** PROJEXA construction-site organizational model
- **Effort:** 1 day (may require Owner input)
- **Affected Repos:** compliance-tracker (role definitions)
- **Notes:** Once defined, used by P0.3a (priority routing) and P6.2 (minimum required role)

#### ESC-D5: P3.1 - Queue Phase Tracking
- **Scope:** How does system distinguish P0/P1/P2 queue "phases"? Define queue_phase enum and routing logic
- **Complexity:** JUDGMENT (queue design decision)
- **Blockers:** ESC-D2 (high-priority role)
- **Depends On:** Queue architecture decision (separate queues? single queue with phase field? priority levels?)
- **Effort:** 1-2 days
- **Affected Repos:** compliance-tracker (task-service, resource_governor)
- **Notes:** Current system has priority field, not phases; may be conflating concepts

#### ESC-D6: P5.2 - Lightweight Presentation Layer Model
- **Scope:** Which "lightweight local model" should translate structured answers to conversational text?
- **Complexity:** JUDGMENT (model selection, infrastructure)
- **Blockers:** None
- **Depends On:** LLM strategy decision (run locally? API call? which model?)
- **Effort:** 1-3 days (depends on infrastructure)
- **Affected Repos:** compliance-tracker (P5 layer), projexa (client-side?), possibly veridian-brain
- **Notes:** "Lightweight" suggests < 1GB model, sub-100ms latency; ORT, ONNX, or small LLM candidate?

### SET E: Complex Subsystem Integration (3 items)

#### ESC-E1: P4.1 - Gap Report Generation
- **Scope:** Service that monitors P3 software execution, detects gaps (missing rules/validations), emits structured gap_report
- **Complexity:** INTEGRATIVE + JUDGMENT (new observability layer required)
- **Blockers:** ESC-B2 (gap schema), ESC-D3 (confidence criteria)
- **Depends On:** Task execution instrumentation
- **Effort:** 3-5 days
- **Affected Repos:** compliance-tracker, ai-os/scripts
- **Notes:** "Gap Report ONLY" per spec - must capture only deterministic signals, no LLM reasoning yet

#### ESC-E2: P4.2 + P4.3 - AI Patch Loop
- **Scope:** Open-source model reads gap_report, emits patch; software applies patch; re-runs task; validates 100% confidence (max 2 iterations)
- **Complexity:** INTEGRATIVE (multi-service orchestration, AI integration)
- **Blockers:** ESC-E1 (gap reports), ESC-B3 (patch format), ESC-D3 (confidence criteria)
- **Depends On:** AI model selection, patch application framework
- **Effort:** 5-7 days (includes integration testing)
- **Affected Repos:** compliance-tracker, ai-os/scripts, external AI service
- **Notes:** Max 2 iterations enforced; 3rd failure escalates to paid model

#### ESC-E3: P5 - Presentation Layer Implementation
- **Scope:** Software-first layer that formats deterministic answers; optional lightweight model translation for conversational output
- **Complexity:** INTEGRATIVE (may span task-execution-engine, presentation-service, P5 layer)
- **Blockers:** ESC-D6 (model selection)
- **Depends On:** Task response schema standardization
- **Effort:** 2-3 days (assuming model choice is decided)
- **Affected Repos:** compliance-tracker
- **Notes:** P5.3a gate: AI blocked entirely on transactional writes; only on read/query responses

---

## Summary Table

| ESC ID | Description | Type | Complexity | Effort | Blocker | Dependencies |
|--------|-------------|------|-----------|--------|---------|--------------|
| ESC-1 | Fingerprint field | Schema | INTEGRATIVE | 2-3d | None | None |
| ESC-2 | UUID v7 migration | Schema | JUDGMENT | 3-5d | None | DB migration strategy |
| ESC-3 | Registry table | Schema | INTEGRATIVE | 2-3d | ESC-1 | P2.1 API contract |
| ESC-4 | Metrics table | Schema | INTEGRATIVE | 1-2d | None | Sampling strategy |
| ESC-5 | Role field | Schema | JUDGMENT | 1-2d | ESC-D1 | Role hierarchy |
| ESC-B1 | Fingerprint lookup API | API | JUDGMENT | 1-2d | ESC-3 | API design |
| ESC-B2 | Gap report schema | API | JUDGMENT | 2-3d | None | Gap taxonomy |
| ESC-B3 | Patch format | API | JUDGMENT | 2-3d | ESC-B2 | Patch framework |
| ESC-D1 | Source type enum | Decision | JUDGMENT | 0.5-1d | None | Product decision |
| ESC-D2 | High-priority roles | Decision | JUDGMENT | 0.5-1d | ESC-D4 | Role hierarchy |
| ESC-D3 | 100% confidence criteria | Decision | JUDGMENT | 1-2d | None | Owner discussion |
| ESC-D4 | Role hierarchy | Decision | JUDGMENT | 1d | None | Org structure |
| ESC-D5 | Queue phase tracking | Decision | JUDGMENT | 1-2d | ESC-D2 | Queue architecture |
| ESC-D6 | Presentation model | Decision | JUDGMENT | 1-3d | None | Model selection |
| ESC-E1 | Gap generation | Integration | INTEGRATIVE | 3-5d | ESC-B2, ESC-D3 | Instrumentation |
| ESC-E2 | Patch loop | Integration | INTEGRATIVE | 5-7d | ESC-E1, ESC-B3 | AI model, framework |
| ESC-E3 | Presentation layer | Integration | INTEGRATIVE | 2-3d | ESC-D6 | Response schema |

**Total Effort:** ~36-62 person-days across all 17 escalation items

**Critical Path:** ESC-D1 → ESC-D4 → ESC-D2 → ESC-D5 → ESC-1 → ESC-3 → ESC-B1 (and parallel: ESC-B2 → ESC-B3 → ESC-E2; ESC-D6 → ESC-E3)

---

## Next Action

Per spec: "If a step cannot resolve to TRUE or FALSE with evidence, you STOP and record an ESCALATION. Escalating is SUCCESS."

**Escalations recorded above.** All 17 items registered with:
- Scope clearly defined
- Complexity honestly labeled as JUDGMENT or INTEGRATIVE
- Blockers and dependencies documented
- No items artificially downgraded to mechanical to save effort

This is the correct outcome per the spec. Implementation should not proceed on any of these items without explicit Owner/PO decision on each design point and approval of the schema changes.

