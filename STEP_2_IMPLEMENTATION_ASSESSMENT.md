# Step 2 Implementation Assessment

**Criteria for Implementation:**
- a) Status is MISSING or EXISTS_STUB, AND
- b) Protocol fully determines behavior (no design/judgment), AND
- c) No new database schema required, AND
- d) No new cross-repo contracts, AND
- e) Does not resolve a DUPLICATE

---

## Item-by-Item Assessment

### P0.1: Input tagged with source type
- Status: EXISTS_STUB
- (a) ✅ YES
- (b) ❌ NO - Protocol doesn't define what source types exist (human/API/machine_sensor/AI_agent/link_click)
- **Decision:** ESCALATE - Design decision needed on enum values
- **Child Work Item:** "Define input source type enum and implement in tasks.source_type field"

### P0.2: SHA-256 fingerprint
- Status: MISSING
- (a) ✅ YES
- (b) ✅ YES - Fully determined: SHA-256(tenant_id + role_level + MODE_PILL + OPTION_SELECTION + CHAT)
- (c) ❌ NO - Requires tasks.fingerprint field (schema change)
- **Decision:** ESCALATE - Schema required
- **Child Work Item:** "Add fingerprint column and generate SHA-256 at P0 ingestion point"

### P0.3: UUID v7 allocation
- Status: MISSING
- (a) ✅ YES
- (b) ✅ YES - Fully determined: use UUID v7 per RFC
- (c) ❌ UNKNOWN - Needs investigation: Can tasks table change ID generation?
- **Decision:** ESCALATE - Must determine if backwards-compatible; likely requires migration
- **Child Work Item:** "Migrate tasks.id from createId() to UUID v7"

### P0.3a (GATE): High-priority role source routing
- Status: MISSING
- (a) ✅ YES
- (b) ❌ NO - "High-priority role" undefined; no role hierarchy provided
- **Decision:** ESCALATE - Design decision needed
- **Child Work Item:** "Define high-priority roles and implement P0.3a gate logic"

### P1.1: Local browser cache
- Status: EXISTS_STUB
- (a) ✅ YES
- (b) ✅ YES - Protocol fully specifies: cache by fingerprint, return under 400ms
- (c) ❌ NO - Blocked by P0.2 (fingerprint must exist first)
- **Decision:** BLOCKED - Awaits P0.2 implementation
- **Child Work Item:** "Implement fingerprint-keyed browser cache in projexa"

### P1.1a (GATE): Fingerprint exists locally AND version active
- Status: UNVERIFIABLE (depends on P0.2 + P1.1)
- **Decision:** BLOCKED - Awaits P0.2 and P1.1
- **Child Work Item:** "Implement P1.1a gate logic after P0.2/P1.1"

### P2.1: Global lookup
- Status: MISSING
- (a) ✅ YES
- (b) ✅ YES - Protocol specifies: query server registry by (fingerprint + tenant_id)
- (c) ❌ NO - Requires fingerprint_registry table or column (schema change)
- (d) ❌ MAYBE - May require compliance-tracker API changes
- **Decision:** ESCALATE - Schema and possibly API contract required
- **Child Work Item:** "Implement server-side fingerprint registry and lookup API"

### P2.1a (GATE): Registry holds fingerprint
- Status: MISSING
- **Decision:** BLOCKED - Awaits P2.1
- **Child Work Item:** "Implement P2.1a gate verification"

### P3.1: Priority queue (P0 > P1 > P2)
- Status: EXISTS_STUB
- (a) ✅ YES
- (b) ❌ NO - Protocol doesn't define how to distinguish P0/P1/P2 queue phases in code
- (c) ❌ MAYBE - Requires queue_phase enum or field
- **Decision:** ESCALATE - Design decision needed; queue phase tracking not currently in schema
- **Child Work Item:** "Implement queue phase tracking and P0>P1>P2 routing"

### P3.2: Deterministic software execution
- Status: EXISTS_PARTIAL
- (a) ✅ PARTIAL - System exists but determinism not verified
- **Decision:** NEEDS VERIFICATION - Exercise the system and measure
- **Action:** Part of Step 3 (end-to-end verification)

### P3.3a (GATE): Exactly 100% confidence
- Status: MISSING (system uses 0.95)
- (a) ✅ YES
- (b) ❌ NO - "EXACTLY 100% ... evidenced by schema match + index used + historical success" is design-heavy
  - What is "schema match"? An exact schema/type signature match? JSON schema validation?
  - What "index used"? An inverted index, vector index, database index?
  - What "historical success"? Hit rate? All prior runs succeeded?
  - How to PROVE these without fabricating evidence?
- **Decision:** ESCALATE - Significant design decision; cannot implement "as written" without guessing
- **Child Work Item:** "Define 100% confidence evidence criteria and implement P3.3a gate"

### P4.1: Open-source model receives GAP REPORT
- Status: MISSING
- (a) ✅ YES
- (b) ❌ NO - Requires:
  - GAP REPORT schema definition
  - Decision on which open-source model
  - What "gap" means (missing rule? missing index? missing validation?)
- **Decision:** ESCALATE - Significant design and cross-repo work
- **Child Work Item:** "Design and implement gap-report generation and AI patch loop"

### P4.2: AI emits config patch
- Status: MISSING
- (a) ✅ YES
- (b) ❌ NO - Requires:
  - Rules configuration schema
  - Decision on patch format (YAML? JSON? SQL?)
  - Confidence threshold for when to escalate to paid model
- **Decision:** ESCALATE - Design-heavy
- **Child Work Item:** "Design configuration patch format and AI integration"

### P4.3: Software integrates patch and retries
- Status: MISSING
- (a) ✅ YES
- (b) ❌ NO - Requires:
  - Patch application logic
  - Retry orchestration
  - Iteration counter and MAX 2 loop enforcement
- **Decision:** ESCALATE - Implementation complexity
- **Child Work Item:** "Implement patch application and retry loop with max 2 iterations"

### P4.3a (GATE): Score now 100% after patch
- Status: MISSING
- **Decision:** BLOCKED - Awaits P3.3a (100% confidence definition) and P4.3
- **Child Work Item:** "Implement P4.3a gate after patch loop logic"

### P5.1: Deterministic answer
- Status: EXISTS_PARTIAL
- (a) ✅ PARTIAL
- **Decision:** VERIFICATION ONLY - Part of Step 3 testing
- **Action:** Exercise the running product

### P5.2: Presentation layer (lightweight model translation)
- Status: EXISTS_STUB
- (a) ✅ YES
- (b) ❌ NO - Requires:
  - Definition of "lightweight local model" (which model? How small?)
  - Decision on when to invoke vs direct software output
  - Schema for structured -> conversational translation
- **Decision:** ESCALATE - Design decision
- **Child Work Item:** "Select lightweight model and implement P5.2 translation layer"

### P5.3a (GATE): Transactional write protection
- Status: EXISTS_PARTIAL
- (a) ✅ PARTIAL
- **Decision:** VERIFICATION ONLY - Part of Step 3 testing
- **Action:** Verify write-gate enforcement

### P6.1: Persist locally and globally
- Status: EXISTS_PARTIAL
- (a) ✅ PARTIAL
- (b) ✅ YES - Protocol fully specifies
- (c) ❌ NO - Blocked by P0.2 (need fingerprint column)
- **Decision:** BLOCKED - Awaits P0.2
- **Action:** After P0.2, verify sync is working

### P6.2: Minimum role attached
- Status: EXISTS_PARTIAL
- (a) ✅ PARTIAL
- (b) ❌ NO - "Minimum role level required to execute" - no role hierarchy provided
- **Decision:** ESCALATE - Design decision (role levels)
- **Child Work Item:** "Define role hierarchy and implement minimum_required_role field"

### P6.3: Replay under 400ms
- Status: UNVERIFIABLE
- **Decision:** MEASUREMENT ONLY - Part of Step 3 verification
- **Action:** Exercise the system and measure latency

### P7.1: Track metrics (local hit, global hit, gap fill)
- Status: MISSING
- (a) ✅ YES
- (b) ✅ YES - Protocol fully specifies: ratios across tenants
- (c) ❌ NO - Requires metrics/observability table (schema)
- **Decision:** ESCALATE - Schema required
- **Child Work Item:** "Add metrics table and implement P7.1 tracking"

### P7.2a (GATE): >95% handled without patch loop
- Status: UNVERIFIABLE
- **Decision:** MEASUREMENT ONLY - Part of Step 3 verification
- **Action:** Measure from metrics after P7.1 implementation

---

## SUMMARY

| Category | Count | Impact |
|----------|-------|--------|
| **IMPLEMENTABLE (meets all 5 criteria)** | 0 | None |
| **BLOCKED (by other items)** | 4 | P1.1, P2.1a, P6.1, P6.3 |
| **ESCALATE (design/schema needed)** | 14 | P0.1, P0.2, P0.3, P0.3a, P3.1, P3.3a, P4.1-P4.3a, P5.2, P6.2, P7.1 |
| **VERIFICATION ONLY** | 5 | P3.2, P5.1, P5.3a, P6.3, P7.2a |

---

## ESCALATIONS NEEDED

All 14 items requiring escalation are **JUDGMENT-class work**, per the spec. They require:

1. **Schema design** (5 items): P0.2, P0.3, P2.1, P7.1, possibly P6.2
2. **Business decision** (6 items): P0.1, P0.3a, P3.3a, P3.1, P5.2, P6.2
3. **Complex integration** (3 items): P4.1-P4.3a (entire gap-report/patch-loop subsystem)

These should be registered as child work items with **integrative/judgment complexity**, not mechanical.

