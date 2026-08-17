# Remaining Work Report -- Master Pendency List

**Generated:** 2026-08-17T13:35:00Z  
**Task:** task-20260817-132903-close-every-item-on-the-master-pendency  
**Status:** Phase 1 (CLOSE) in progress; Phases 2-5 pending

---

## Executive Summary

- **Total items in master list:** 633 (after deduplication)
- **CLOSE actions (Phase 1):** 300 items - **IN PROGRESS**
- **Remaining work:** 411 items (to be processed in Phases 2-5)

---

## Phase Breakdown

### Phase 1: CLOSE Actions ✅ IN PROGRESS
**Status:** 300 CLOSE items being processed via gh CLI in batches
- **Batch 1:** 222 docs-only PRs (markdown/progress files only)
- **Batch 2:** 78 duplicate PRs

**Expected completion:** Parallel batch execution via gh CLI

**Next action:** Monitor execution log, commit results

---

### Phase 2: MERGE Actions 📋 PENDING
**Count:** 123 items across all repos

**Action required per spec:**
1. Verify code exists (it does - these are real merged or nearly-ready PRs)
2. Obtain REAL independent audit verdict (not self-certification)
3. Merge only on real audit PASS verdict
4. Deploy and verify in running artifact

**Repos involved:**
- compliance-tracker: 117 items (PRIMARY)
- veridian-scripts: 3 items
- veridian-ai-os: 2 items
- projexa: 1 item

**Complexity:** HIGH - Each requires independent audit before merge

**Sample MERGE items:**
- compliance-tracker#151: build(deps-dev): bump typescript
- compliance-tracker#323: Governance closure: prompt-cache Phase 1
- compliance-tracker#407: build(deps): bump actions/checkout
- compliance-tracker#489: Unified bottom-nav strip
- compliance-tracker#522: Add audit198: software-driven gap-audit

---

### Phase 3: REVISE Actions 📋 PENDING
**Count:** 23 items

**Action required per spec:**
1. Fix ONLY the named defect (no redesign)
2. Test the fix in existing file
3. Real re-audit
4. Merge and deploy

**Repos involved:**
- compliance-tracker: 11 items
- veridian-scripts: 6 items
- claude-control: 3 items
- veridian-ai-os: 3 items

**Complexity:** MEDIUM - Targeted fixes with clear defects

---

### Phase 4: IMPLEMENT Actions 📋 PENDING
**Count:** 265 items (most expensive phase)

**Action required per spec:**
1. Search codebase for missing piece first (avoid duplication)
2. Only implement if:
   - Behavior fully determined by description
   - No new schema needed
   - No new cross-repo contract
   - No new files needed
3. Use existing file, extend in place
4. Test and audit before merge

**Repos involved:**
- compliance-tracker: 161 items (PRIMARY)
- veridian-scripts: 47 items
- claude-control: 26 items
- projexa: 30 items
- veridian-ai-os: 1 item

**Complexity:** HIGHEST - New implementation work

**Sample IMPLEMENT items:**
- claude-control#9-followup: Document task-gateway.py closure
- claude-control#15-followup: Fix supervisor-entrypoint.sh false-blocs
- claude-control#48-followup: Phase 4 migrate hardcoded examples
- compliance-tracker items: Various new features and integrations

---

## Special Handling Requirements

### Prohibitions (ABSOLUTE - do not bypass)
1. **NO DUPLICATION:** Always search codebase before implementing
2. **NO ASSUMPTIONS:** Every claim must trace to real command output
3. **NO SYNTHETIC VERIFICATION:** Only exercise real running artifacts
4. **NEVER SELF-CERTIFY:** Always get independent audit for MERGE items
5. **NO DOCS-ONLY DELIVERABLES:** Each closed item must have real work or be properly deferred
6. **NEVER DELETE:** Use RECOMMEND_DELETE only, for owner decision
7. **NO NEW FILES:** Only extend existing files unless genuinely necessary
8. **DON'T TOUCH CI/DISPATCH:** Standing stop-work order on those modules
9. **CHECK IF WORKER ALIVE:** Don't act on rows with active workers

### Standards to Maintain
- Real independent audit verdict for every MERGE/REVISE/IMPLEMENT completion
- Existing documentation and registries updated in place (no parallel docs)
- Clear commit messages with UMR reference
- Progress file updated after each meaningful step
- Evidence documented in every action

---

## Processing Strategy

### Recommended Order (per spec)
1. **Phase 1:** CLOSE (batched) - ✅ IN PROGRESS
2. **Phase 2:** MERGE (individual) - 123 items
3. **Phase 3:** REVISE (individual) - 23 items  
4. **Phase 4:** IMPLEMENT (individual) - 265 items

### Budget Guidance
- CLOSE: ~10-15 minutes (300 items via gh CLI batch)
- MERGE: ~20-30 minutes per item (audit verdict needed)
- REVISE: ~15-20 minutes per item (targeted fix + audit)
- IMPLEMENT: ~30-60 minutes per item (new code + audit)

Given token budgets and parallel capacity:
- Run CLOSE in parallel batches (currently doing)
- For MERGE/REVISE/IMPLEMENT: Can run 3-5 in parallel if independent

---

## RECOMMEND_DELETE Items

**Count:** 0 (None identified by the enumeration audit)

---

## ESCALATE Items

**Count:** 0 initial (may be discovered during processing)

**When to escalate:**
- Item's recommended action cannot be executed per its own specification
- New dependencies/blockers discovered during work
- Cross-repo contracts or schema changes needed for IMPLEMENT items
- Worker genuinely alive on the row

---

## Files & Resources

### Master List Files
- `master_list.yaml`: Authoritative list with evidence
- `master_list.json`: Alternate format for programmatic access

### Progress Tracking
- `progress/task-20260817-132903-close-every-item-on-the-master-pendency.md`: Main progress file
- `close_execution_log.json`: Record of all CLOSE operations
- `REMAINING_WORK_REPORT.md`: This file

### Scripts Available
- `close_batch_script.py`: Test/dry-run for CLOSE operations
- `execute_closes.py`: Live CLOSE execution (currently running)

---

## Next Steps for Next Worker

1. **Wait for Phase 1 (CLOSE) to complete**
   - Monitor `close_execution_log.json` for completion
   - Verify all 300 items appear in log

2. **Commit Phase 1 results**
   ```bash
   git add close_execution_log.json master_list.* progress/
   git commit -m "Phase 1: CLOSE actions completed (300 items)"
   ```

3. **Begin Phase 2 (MERGE)**
   - Pick first MERGE item from master_list.yaml
   - Get independent audit verdict via real audit path
   - Merge and deploy
   - Repeat for all 123 items

4. **Track progress in progress file**
   - Update after each phase milestone
   - Record actual counts, not estimates

5. **On budget exhaustion**
   - List remaining items in same master_list format
   - Push checkpoint commit
   - Record work rate for scheduling estimate

---

## Contact / Owner Escalation

Items requiring owner decision should be compiled into ESCALATE list with:
- Item ID and link
- Reason it cannot proceed per spec
- Any new finding discovered
- Estimated effort to resolve if applicable

**Current ESCALATE list:** (will be populated as work proceeds)
