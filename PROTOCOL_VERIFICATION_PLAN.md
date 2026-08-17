# Protocol Verification Plan -- Universal Task Architecture (UTA)

## Scope Definition

**Product:** ONE ERP spanning three repositories
**Frontend:** construction-branded public site (thin frontend)
**Task:** Verify all P0-P7 protocol phases are implemented; implement missing gaps

## Three Repositories (To Identify)

- [ ] Repo 1: ?
- [ ] Repo 2: ?
- [ ] Repo 3: ?

## Protocol Phases to Verify

### P0: INGESTION
- P0.1: Every input captured and tagged with source type
- P0.2: Deterministic fingerprint (SHA-256 hash) of: tenant_id + user_role_level + MODE_PILL + OPTION_SELECTION + CHAT
- P0.3: UUID v7 task id allocated and bound to fingerprint
  - **GATE P0.3a:** Is source high-priority role?

### P1: LOCAL LOOKUP (target: 95% of tasks)
- P1.1: Local browser-side task cache queried by fingerprint
  - **GATE P1.1a:** Fingerprint exists locally AND version is active?

### P2: GLOBAL LOOKUP (remaining ~5%)
- P2.1: Fingerprint + tenant_id sent to central server
  - **GATE P2.1a:** Global registry holds this fingerprint?

### P3: SOFTWARE-FIRST EXECUTION
- P3.1: Task enters priority queue (P0 > P1 > P2)
- P3.2: Deterministic engine of pure code attempts task
  - **GATE P3.3a:** Software confidence is EXACTLY 100% (evidenced by schema match, index used, historical success)?

### P4: AI EVALUATION AND PATCH LOOP
- P4.1: Open-source model receives GAP REPORT ONLY
- P4.2: Model emits software configuration patch (rules data)
  - If confidence < 100%, escalate to paid high-end model
- P4.3: Software integrates patch and re-runs original task
  - **GATE P4.3a:** Software now scores 100%? (FALSE → loop max 2x, then escalate; TRUE → dismiss AI)

### P5: PRESENTATION LAYER
- P5.1: Software produces exact deterministic answer
- P5.2: Lightweight local model translates to conversational sentence
  - **GATE P5.3a:** Is this a transactional write? (TRUE → AI blocked; FALSE → local model may format)

### P6: STORAGE, VERSIONING, SYNC
- P6.1: Task id and fingerprint persist to LOCAL STORE and SERVER REGISTRY
- P6.2: Minimum role level required attached
- P6.3: Later users with sufficient rights replay stored output <400ms, zero rework, no AI

### P7: SUPERVISOR
- P7.1: Track ratios of local hit, global hit, software gap fill across tenants
  - **GATE P7.2a:** Software (including cache replays) handles >95% without patch loop?

## Status Matrix Template

| Item | Status | Evidence / Code Location | Notes |
|------|--------|--------------------------|-------|
| P0.1 | ? | | |
| P0.2 | ? | | |
| P0.3 | ? | | |
| P0.3a (GATE) | ? | | |
| P1.1 | ? | | |
| P1.1a (GATE) | ? | | |
| ... | | | |

## Search Strategy

1. **compliance-tracker repo:** Search for cache, fingerprint, task-id patterns
2. **projexa repo:** Search for frontend logic, input ingestion
3. **Third repo:** Identify and search
4. **ai-os scripts:** Search for backend registry, storage, dispatch logic

---

**Next Step:** Identify three repos, then fill matrix with EXISTS_REAL / EXISTS_STUB / EXISTS_PARTIAL / DUPLICATE / MISSING / UNVERIFIABLE status for each protocol item.
