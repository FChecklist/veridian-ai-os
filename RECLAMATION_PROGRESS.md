# Disk Reclamation: Task Workspace Cleanup
Task: task-20260817-184059-reclaim-terminal-task-workspace-disk-spa
UMR: UMR-20260817-184053-f874
Reference: UMR-20260807-075748-3f33 (previous successful run)

## Status: IN PROGRESS

## Current State (Before Reclamation)
- **Date**: 2026-08-17 18:40:59 UTC
- **Disk Usage**: 266GB / 301GB (93% - 23GB avail)
- **Task Count**: 2233 total analyzed, 577 with terminal status + workspace
- **Procedure**: Exact reuse of UMR-20260807-075748-3f33

## Analysis Results
- Total tasks checked: 2233
- Tasks with terminal status (completed, completed_unmerged, failed, killed, rejected_duplicate): 577
- Tasks with workspaces to delete: 577
- Estimated total size to reclaim: ~34GB (577 tasks × ~60MB avg)

## Completion Checklist

### Phase 1: Analysis ✓
- [x] Identify all task directories
- [x] Check terminal status in task.yaml
- [x] Assess workspace presence
- [x] Estimate total reclaimable space

### Phase 2: Deletion (IN PROGRESS)
- [ ] Create deletion script
- [ ] Execute workspace deletions
- [ ] Verify all deletions completed
- [ ] Track per-item decisions

### Phase 3: Log Truncation
- [ ] Identify applicable oneshot systemd logs
- [ ] Check for dispatch-tick-cron.log (like 3f33)
- [ ] Verify no live file descriptors
- [ ] Truncate in-place if applicable

### Phase 4: Verification & Audit
- [ ] Verify disk space reclaimed
- [ ] Record final df -h
- [ ] Generate deletion report
- [ ] Independent AUDIT:PASS verification

### Phase 5: Cleanup & Commit
- [ ] Commit changes
- [ ] Record completion with agent_work_briefing.py

## Notes
- Not modifying: task.yaml, PROGRESS.md, progress/, result.json, worker.log
- Not touching: /opt/veridian/backups/*, /opt/veridian/repos/*, live databases
- Real execution required (not dry-run)
- Per-item table will show task, decision, and reason for each deletion

---
Last updated: 2026-08-17 18:40:59 UTC
