# PROGRESS -- task-20260807-084726-disk-emergency-at-94-percent-with-20g-fr

## Completed
- [x] Read prior UMR-20260807-001537-787a, UMR-20260807-001650-d266, UMR-20260806-183112-e274
      evidence (umr_tasks rows + /opt/veridian/ai-os/reports/*.json). Real procedure identified:
      delete ONLY workspace/ subdir of a task dir whose task.yaml status is terminal, gated by
      (a) systemctl --user is-active <service> not active, (b) git status --porcelain clean,
      (c) no unpushed commits / has upstream. Never touch task.yaml/governance files. This is
      the same pattern reused across all three prior UMRs (d6d6 -> e274 -> 787a lineage).
- [x] Verified live DB integrity myself RIGHT NOW: `PRAGMA integrity_check` = **ok** (page_count
      992941, freelist_count 390455 @ 4096B pages = 4.07GB total / ~1.5GB freelist-reclaimable via
      VACUUM). NOTE: two prior UMRs (787a, d266) independently found this SAME db FAILED
      integrity_check ~8h ago (malformed wiring_registry index) -- it has evidently been repaired
      since then. Current live state re-verified directly, not assumed from spec text.
- [x] Confirmed dispatch-tick-cron.log content directly: tail is a full JSON state dump
      (real_task_counts, blocked-task list, etc.) re-appended in full every cron tick, not an
      incremental event log -- corroborates spec's claim.
- [x] Step 1 breakdown (scoped du, see report) -- ai-os/memory 20.2G (backups/ 11.4G + live
      sqlite 4.07G + a stray corrupt-DB snapshot copy 4.07G + all_server_files txt 383M), ai-os/logs
      632M (dispatch-tick-cron.log 413M dominant), ai-os/tasks: 1582 real task dirs (matches spec's
      1566 claim, grown since -- confirmed with 3x repeated `ls` for consistency after an initial
      racy read). node_modules under tasks: 63 dirs total, but 0 bytes reclaimable via the
      sanctioned prune_task_node_modules.py dry-run (all 63 belong to non-terminal tasks; the
      script's own self-prune-on-checkpoint wiring already keeps terminal-task node_modules at
      zero, confirmed live, not assumed).
- [x] Ran sanctioned prune_task_node_modules.py --dry-run: 0 bytes/0 dirs eligible (real result,
      not a failure -- see above).

## Remaining
- [ ] Step 2: run workspace/ reclamation (dry-run in progress/done, then real run), report real
      bytes reclaimed + df before/after
- [ ] Step 3a: VACUUM superboss-register.sqlite via superboss-register.py (real backup first,
      quiescent), ~1.5GB expected reclaim -- ONLY if disk headroom is sufficient after step 2
- [ ] Step 3b: decide + act on dispatch-tick-cron.log (truncate in place, preserve inode, do not
      delete/rename since it's actively written every cron tick)
- [ ] Final df before/after table + per-item bytes-reclaimed table
- [ ] record-completion call to agent_work_briefing.py
