# task-20260818-025859-implement--for-real--not-a-progress-note

Governing: UMR-20260818-025834-fa54. Fixes the real AUDIT:FAIL from
UMR-20260817-182858-106d (prior worker wrote only PROGRESS.md, never the
real script). Implements the R1-R4 retention policy exactly as documented
in UMR-20260808-023802-1955's report
(`/opt/veridian/ai-os/reports/backup-tree-inventory-retention-proposal-UMR-20260808-023802-1955.md`)
-- numbers/rules read from that report, not re-derived.

## Completed

- [x] Read the governing report (UMR-20260808-023802-1955) in full; confirmed R1-R4 wording and the worked Tree1/Tree2 numbers, used verbatim (not re-derived).
- [x] Checked `reconcile_stale_running_workers.py`'s real location to decide the correct repo home: it lives at the ROOT of `/opt/veridian/repos/veridian-scripts` (no `scripts/` subdirectory in that repo). Attempted to write there; **blocked by this box's own `pretooluse_worker_enforcement` hook** ("Write targets ... outside this worker's own assigned workspace"). This worker's assigned workspace is the `veridian-ai-os` checkout, so the file is placed at `scripts/prune_backup_trees.py` within it -- the literal path the TARGET named, and the only repo this worker is actually permitted to write into.
- [x] Confirmed `/opt/veridian/repos/veridian-scripts/prune_memory_backups.py` already exists (keep-N-most-recent-VERIFIED policy, own systemd timer, memory-dir-root + memory/backups scope, superboss-register.sqlite only) -- a genuinely DIFFERENT policy from the R1-R4 same-day-dedup rule this task implements. Left completely untouched; this new script does not conflict with or replace it.
- [x] **Created the real script**: `scripts/prune_backup_trees.py` (~340 lines). Implements:
  - R1 (never delete live DB/-wal/-shm/single most-recent backup per source-DB per tree)
  - R2 (same-day dedup, keep only the most-recent same-day snapshot)
  - R3 (never remove the sole backup of any calendar day)
  - R4 (fresh read-only `PRAGMA quick_check` on the implicated live DB(s) immediately before any deletion in a tree; a failing check aborts THAT TREE's deletions only -- reported, not a crash; an unrelated source DB with nothing pending deletion in that tree is never checked/never blocks it)
  - R1+R2+R3 implemented as one collapsed rule (see module docstring for the proof): keep the max-mtime group per (source_db, tree, UTC calendar day).
  - Dry-run is the default; `--execute` is the only way any deletion happens.
  - Applies to both real trees named in the report: `/opt/veridian/backups/sqlite-daily` and `/opt/veridian/ai-os/memory/backups`, for both real source DBs (`superboss-register.sqlite`, `credit-ledger.sqlite`).
- [x] **Created real tests**: `tests/test_prune_backup_trees.py`, 18 tests, all passing (`python3 -m pytest tests/test_prune_backup_trees.py -v` -> 18 passed). Covers R1, R2 (plan + real `--execute` deletion), R3, R4 (abort case, per-tree-not-global abort, only-implicated-DB-is-checked), a dedicated dry-run-has-zero-side-effects test (directory listing + per-file size/mtime unchanged, even against a corrupt live DB), -wal/-shm companion grouping, live-DB-self-protection, and CLI/subprocess-level tests (default dry-run, `--execute` success, `--execute` R4-abort exit code 1, bad-argument exit code 2).
- [x] Ran a **real dry-run against the real trees** (read-only, no `--execute` -- the ABSOLUTE PROHIBITION in this task's own SPEC was honored throughout, never violated). Real output below.
- [x] Committed the real code + tests (this file included) and pushed.

## Real dry-run output against the real trees (2026-08-18T03:07:57Z)

Command: `python3 scripts/prune_backup_trees.py` (no `--execute`).

```
=== tree: /opt/veridian/backups/sqlite-daily  (R4 OK) ===
  R4 quick_check[superboss-register.sqlite]: ok (ok) live_db=/opt/veridian/ai-os/memory/superboss-register.sqlite
  kept           rule=R1 bytes=     2,920,448 day=2026-08-07 path=/opt/veridian/backups/sqlite-daily/credit-ledger.sqlite.20260807.bak
  kept           rule=R1 bytes= 1,810,980,864 day=2026-08-06 path=/opt/veridian/backups/sqlite-daily/superboss-register.sqlite.20260806-100057Z-fresh.bak
  would-delete   rule=R2 bytes= 1,614,348,288 day=2026-08-06 path=/opt/veridian/backups/sqlite-daily/superboss-register.sqlite.20260806.bak
  would-delete   rule=R2 bytes= 1,661,845,504 day=2026-08-06 path=/opt/veridian/backups/sqlite-daily/superboss-register.sqlite.20260806T044325Z-pre-swap-fresh.bak
  would-delete   rule=R2 bytes= 1,638,092,800 day=2026-08-06 path=/opt/veridian/backups/sqlite-daily/superboss-register.sqlite.20260806T043818Z-pre-file_inventory-recover-fresh.bak
  would-delete   rule=R2 bytes= 1,588,728,024 day=2026-08-06 path=/opt/veridian/backups/sqlite-daily/superboss-register.sqlite.20260806-pre-recover.bak   (main 1,574,633,472 B + its -wal sidecar 14,094,552 B, deleted as one group)
  kept           rule=R3 bytes=     2,887,680 day=2026-08-06 path=/opt/veridian/backups/sqlite-daily/credit-ledger.sqlite.20260806.bak
  kept           rule=R3 bytes= 1,445,003,264 day=2026-08-05 path=/opt/veridian/backups/sqlite-daily/superboss-register.sqlite.20260805.bak
  kept           rule=R3 bytes=     2,871,296 day=2026-08-05 path=/opt/veridian/backups/sqlite-daily/credit-ledger.sqlite.20260805.bak
  kept           rule=R3 bytes=     2,842,624 day=2026-08-04 path=/opt/veridian/backups/sqlite-daily/credit-ledger.sqlite.20260804.bak
  kept           rule=R3 bytes=   508,792,832 day=2026-08-03 path=/opt/veridian/backups/sqlite-daily/superboss-register.sqlite.20260803.bak
  kept           rule=R3 bytes=     2,805,760 day=2026-08-03 path=/opt/veridian/backups/sqlite-daily/credit-ledger.sqlite.20260803.bak
  kept           rule=R3 bytes=   184,225,792 day=2026-08-02 path=/opt/veridian/backups/sqlite-daily/superboss-register.sqlite.20260802.bak
  kept           rule=R3 bytes=     2,772,992 day=2026-08-02 path=/opt/veridian/backups/sqlite-daily/credit-ledger.sqlite.20260802.bak
  kept           rule=R3 bytes=    65,736,704 day=2026-08-01 path=/opt/veridian/backups/sqlite-daily/superboss-register.sqlite.20260801.bak
  kept           rule=R3 bytes=     2,670,592 day=2026-08-01 path=/opt/veridian/backups/sqlite-daily/credit-ledger.sqlite.20260801.bak
  kept           rule=R3 bytes=    58,634,240 day=2026-07-30 path=/opt/veridian/backups/sqlite-daily/superboss-register.sqlite.20260730.bak
  kept           rule=R3 bytes=     2,428,928 day=2026-07-30 path=/opt/veridian/backups/sqlite-daily/credit-ledger.sqlite.20260730.bak
  kept           rule=R3 bytes=    57,290,752 day=2026-07-29 path=/opt/veridian/backups/sqlite-daily/superboss-register.sqlite.20260729.bak
  kept           rule=R3 bytes=     2,428,928 day=2026-07-29 path=/opt/veridian/backups/sqlite-daily/credit-ledger.sqlite.20260729.bak
  kept           rule=R3 bytes=    47,329,280 day=2026-07-26 path=/opt/veridian/backups/sqlite-daily/superboss-register.sqlite.20260726.bak
  kept           rule=R3 bytes=     1,966,080 day=2026-07-26 path=/opt/veridian/backups/sqlite-daily/credit-ledger.sqlite.20260726.bak
  kept           rule=R3 bytes=    47,329,280 day=2026-07-25 path=/opt/veridian/backups/sqlite-daily/superboss-register.sqlite.20260725.bak
  kept           rule=R3 bytes=     1,966,080 day=2026-07-25 path=/opt/veridian/backups/sqlite-daily/credit-ledger.sqlite.20260725.bak
  kept           rule=R3 bytes=     9,945,088 day=2026-07-24 path=/opt/veridian/backups/sqlite-daily/superboss-register.sqlite.20260724.bak
  -- would_delete_bytes=6,503,014,616 deleted_bytes=0

=== tree: /opt/veridian/ai-os/memory/backups  (R4 OK) ===
  R4 quick_check[superboss-register.sqlite]: ok (ok) live_db=/opt/veridian/ai-os/memory/superboss-register.sqlite
  kept           rule=R1 bytes= 4,067,086,336 day=2026-08-06 path=/opt/veridian/ai-os/memory/backups/superboss-register.sqlite.pre-fullfile-backup-20260806T193901Z
  would-delete   rule=R2 bytes= 4,067,119,104 day=2026-08-06 path=/opt/veridian/ai-os/memory/backups/superboss-register.sqlite.pre-fullfile-backup-20260806T193627Z
  would-delete   rule=R2 bytes= 4,067,119,104 day=2026-08-06 path=/opt/veridian/ai-os/memory/backups/superboss-register.sqlite.pre-fullfile-backup-20260806T193316Z
  -- would_delete_bytes=8,134,238,208 deleted_bytes=0
```

Real, live PRAGMA quick_check on the live `superboss-register.sqlite` returned `ok` in both trees' R4 gates (fresh checks, run at execution time, not cached). Combined `would_delete_bytes` this run: 14,637,252,824 B (~13.63 GiB) -- matches the report's original ~13.6 GiB estimate to within 65,536 B (two backup files each grew by exactly one 32,768-byte SQLite page in the 10 days since the report's 2026-08-08 snapshot; every removal candidate's identity/rule assignment is otherwise identical to the report's Section 5 worked example). No `--execute` was ever run against these real paths; nothing was deleted.

Tree1 `superboss-register.sqlite.20260806-pre-recover.bak` group's reported bytes (1,588,728,024) is the main file (1,574,633,472 B) plus its `-wal` sidecar (14,094,552 B) deleted as one unit -- matches the report's own 5-file, 6,503,014,616-byte Tree1 removal set exactly.

## Remaining

- [ ] Independent AUDIT:PASS (external gate, not self-certifiable by this worker).
- [ ] Real PR opened by the automated pipeline (this worker does not call `gh pr create`) once quality gates + review pass on this diff.
- [ ] Real merge + verification on post-merge main.
- [ ] Call `agent_work_briefing.py record-completion --umr-id UMR-20260818-025834-fa54` once the above are real and confirmed (not yet called -- premature before independent audit/merge).
