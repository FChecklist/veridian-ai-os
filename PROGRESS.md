# PROGRESS -- task-20260808-044537-triage-the-232-failed-umr-tasks-rows-rea

## Completed
- [x] Confirmed 232 rows at status='failed' in superboss-register.sqlite (read-only queries only)
- [x] Exported full failed-row set (232) and running-row set (68) to /tmp/umr_analysis for offline grouping
- [x] Grouped failed rows by source_trigger with counts + date spread (substr ts_submitted)
- [x] Grouped failed rows by task_kind with counts + date spread
- [x] Clustered failed rows by real reason-field content (12 real clusters, not by label)
- [x] Pulled representative reason excerpts for the 5 largest groups (A/B/C/D/E)
- [x] Classified groups: already fixed (2 concrete cases verified live in code) / stale duplicates of later-succeeded work (145+ rows) / real open defects (4 identified, incl. resource_governor.py's still-live _task_yaml_for_umr_row() gap)
- [x] Checked OCID-020 categories 3, 13, 17, 23, 25: only 1 of 232 failed rows touches them (UMR-20260806-115604-3535, real cat17/21 blocker diagnosis); cross-checked live gtm_certification_categories state for all five
- [x] Checked correlation between failed population and running-with-no-worker rows: 67/68 running rows have no real worker (verified live via systemctl --user is-active), and 145 of 232 failed rows are the identical prior-cycle instance of this same phenomenon; concrete retry-loop evidence found (3 repeating task stems)
- [x] Wrote report to /opt/veridian/ai-os/reports/failed-232-triage-UMR-20260808-044511-1b21.md
- [x] record-completion call to agent_work_briefing.py
- [x] Commit + push

## Remaining
(none -- task complete)
