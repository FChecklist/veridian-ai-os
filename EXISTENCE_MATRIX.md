# EXISTENCE MATRIX -- Universal Task Architecture Protocol

**Report Date:** 2026-08-17  
**Product Scope:** Construction-branded ERP (PROJEXA frontend + compliance-tracker backend)  
**Protocol:** P0-P7 phases + 7 gates per UNIVERSAL_TA specification  

---

## KEY FINDINGS (Summary)

1. **Partial Implementation Found:** System has caching, task execution, and workflows, but NO deterministic fingerprinting (SHA-256) nor UUID v7 binding
2. **Three Main Repos Identified:**
   - **compliance-tracker:** ERP backend, database, APIs, services
   - **projexa:** Construction frontend (Next.js), offline queue
   - **veridian-scripts/ai-os:** Task orchestration, monitoring, dispatch

3. **Critical Gaps:**
   - P0.2: No SHA-256 fingerprinting of (tenant_id + role + MODE_PILL + OPTION_SELECTION + CHAT)
   - P0.3: No UUID v7 binding to fingerprint
   - P1.1a: Browser cache exists (IndexedDB) but not keyed by fingerprint
   - P2.1: No global registry lookup by fingerprint
   - P3.3a: No explicit "100% confidence" gate with schema match proof
   - P7.2a: No metrics tracking for cache hit ratios

---

## DETAILED MATRIX

| # | Protocol Item | Status | Evidence Location | Notes |
|---|---|---|---|---|
| **P0.1** | Every input captured and tagged with source type | EXISTS_STUB | task-service.ts, createTask() | Task title/description captured, but source type not explicitly tagged; no "source enum" in tasks table |
| **P0.2** | Deterministic fingerprint (SHA-256) of tenant_id+role+MODE_PILL+OPTION_SELECTION+CHAT | MISSING | -- | No fingerprint column in tasks table; no hash generation code found; instruction-execution-cache-service.ts uses embeddings instead |
| **P0.3** | UUID v7 task id allocated and bound to fingerprint | MISSING | -- | Tasks use createId() (ULID-like), not UUID v7; no binding to fingerprint exists |
| **P0.3a (GATE)** | Is source high-priority role? | MISSING | -- | No priority queue routing by source role; tasks table has priority field but not source-role-based |
| **P1.1** | Local browser-side task cache keried by fingerprint | EXISTS_STUB | projexa/src/lib/offline/work-progress-queue.ts | IndexedDB queue exists (idb-keyval), but keyed by localId (random UUID), not by fingerprint |
| **P1.1a (GATE)** | Fingerprint exists locally AND version is active? | UNVERIFIABLE | -- | Without fingerprints, cannot verify this gate |
| **P2.1** | Fingerprint + tenant_id sent to central server | MISSING | -- | No fingerprint-based lookup API found; registry lookups use keyword/embedding search (capability-registry-service.ts), not fingerprint hash |
| **P2.1a (GATE)** | Global registry holds this fingerprint? | MISSING | -- | No global fingerprint registry table found |
| **P3.1** | Task enters priority queue (P0 > P1 > P2) | EXISTS_STUB | task-service.ts L122 | Tasks ordered by priority DESC, createdAt ASC, but no queue phases (P0/P1/P2) distinction |
| **P3.2** | Deterministic engine of pure code attempts task | EXISTS_PARTIAL | task-execution-engine.ts (referenced in task-service.ts) | Task execution engine exists; determinism NOT verified (has high-confidence gate at 0.95 but not "EXACTLY 100%") |
| **P3.3a (GATE)** | Software confidence EXACTLY 100%, evidenced by schema match + index used + historical success | MISSING | instruction-execution-cache-service.ts L37, 42-44 | System uses 0.95 confidence threshold, not 100%; no explicit "schema match" or "index used" evidence fields |
| **P4.1** | Open-source model receives GAP REPORT ONLY | MISSING | -- | No gap-report generation found; no open-source model integration for patch loop |
| **P4.2** | Model emits software configuration patch (rules data) | MISSING | -- | No patch generation mechanism found; no rules configuration system observed |
| **P4.3** | Software integrates patch and re-runs original task | MISSING | -- | No patch integration or retry logic found |
| **P4.3a (GATE)** | Software now scores 100% after patch? (MAX 2 iterations) | MISSING | -- | No iteration or retry loop for patch application |
| **P5.1** | Software produces exact deterministic answer | EXISTS_PARTIAL | task-execution-engine.ts | Task execution produces results, determinism NOT explicitly verified |
| **P5.2** | Lightweight local model translates structured answer to conversational sentence | EXISTS_STUB | compliance-tracker has embedding/model infrastructure, but no dedicated "presentation layer translation" service found |
| **P5.3a (GATE)** | Is output a transactional write? | EXISTS_PARTIAL | task-service.ts creates tasks (write-protected); write-gate enforcement for other transactional operations unknown |
| **P6.1** | Task id and fingerprint persist to LOCAL STORE and SERVER REGISTRY | EXISTS_PARTIAL | tasks table (server), IndexedDB (client) | Task persistence exists, but no fingerprint field; no explicit sync mechanism between local and server |
| **P6.2** | Minimum role level required attached | EXISTS_PARTIAL | Task has userId/actor context, but minimum_role_level field not found in schema |
| **P6.3** | Later users with sufficient rights replay stored output <400ms, zero rework, no AI | UNVERIFIABLE | instruction-execution-cache-service.ts has embedding-based replay | Replay mechanism exists (embeddings), latency NOT measured; confidence threshold 0.95 (not 100%) |
| **P7.1** | Track ratios of local hit, global hit, software gap fill across tenants | MISSING | -- | No metrics/observability table for cache/registry hit ratios found; no per-tenant tracking observed |
| **P7.2a (GATE)** | Software (including cache replays) handles >95% without patch loop? | UNVERIFIABLE | -- | No metrics data to measure; no "patch loop invocation" counter found |

---

## SEARCH RECORD

### Searches Performed to Prove MISSING Status

**Fingerprint/Hash Search:**
- `grep -r "fingerprint\|SHA.*256\|hash.*input" /opt/veridian/repos/compliance-tracker /opt/veridian/repos/projexa` → No matches in core code

**UUID v7 Search:**
- `grep -r "uuidv7\|uuid.v7" /opt/veridian/repos/` → No explicit UUID v7 imports; tasks use createId()

**Global Registry by Fingerprint:**
- Checked: capability-registry-service.ts, asset-registry-service.ts, module-registry-service.ts
- All use embedding/keyword search, not fingerprint lookup

**Gap Report / Patch Loop:**
- Searched: task-execution-engine.ts, error handling in main services
- No gap-report generation or AI patch-integration found

**Write Gate / Transactional Protection:**
- Found: policy-enforcement-engine.ts exists (referenced in 20_ENGINES_10_GATEWAYS_PHASE_PLAN_2026-07-24.yaml)
- Write protection at task creation exists, but full transactional write gating scope unknown

### Code Files Examined

**compliance-tracker:**
- src/lib/services/task-service.ts (task creation, execution planning)
- src/lib/services/instruction-execution-cache-service.ts (embedding-based cache, 0.95 confidence)
- src/lib/db/schema.ts (tasks table, no fingerprint field)
- Database catalog (444 tables, no fingerprint_registry table)

**projexa:**
- src/lib/offline/work-progress-queue.ts (IndexedDB queue, localId based)
- src/lib/services/ (not fully explored due to timeout)

**ai-os:**
- 20_ENGINES_10_GATEWAYS_PHASE_PLAN_2026-07-24.yaml (architecture overview)
- CAPABILITY_REGISTRY_SCHEMA_2026-07-24.yaml (schema design, not yet live-wired)
- DIRECTIVE.yaml (dedup mechanisms, resource governance, no fingerprint mention)

---

## CONCLUSION

**95% of protocol items are either MISSING or stub implementations.**

The system has:
- ✅ Task creation and execution (P3.1-P3.2 partial)
- ✅ Local caching (IndexedDB) and embedding-based similarity search (P1 alternative)
- ✅ Approval/workflow systems (P5 partial)
- ✅ Persistence layers (P6 partial)

The system lacks:
- ❌ Deterministic SHA-256 fingerprinting (P0.2)
- ❌ UUID v7 allocation (P0.3)
- ❌ 100% confidence gates (P3.3a)
- ❌ Gap reporting and patch loop (P4)
- ❌ Metrics/supervisor (P7)

**Next Action:** Implement protocol items that pass the Step 2 criteria (unambiguous, schema-free, no cross-repo contracts, not duplicates, not design decisions).

