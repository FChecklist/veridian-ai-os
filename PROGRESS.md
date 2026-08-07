# PROGRESS -- task-20260807-054804-governance-integrity--re-adjudicate-320

## Completed

- [x] Step 1: independently re-derived all four PM-measured counts directly against
      `/opt/veridian/ai-os/memory/superboss-register.sqlite` (`PRAGMA integrity_check` = `ok` first).
      All four matched the PM's numbers exactly -- no discrepancy to report:
      - `407` rows `status='failed'` with `reason LIKE '%one-time backfill%'`.
      - `87` of those have no `new_task_id` in `outputs_json` -- left untouched (fair `failed` verdict, confirmed still `failed` post-run).
      - `320` of those DO carry a real `outputs_json.new_task_id`, and **all 320** (zero missing) have a real
        directory on disk under `/opt/veridian/ai-os/tasks/<new_task_id>/`.
      - `60` of the 320 were submitted on/after `2026-08-06`.
      - (Also found, not asked for but relevant: the "Stage 1" backfill actually ran **three** separate times --
        `2026-08-06T08:29:07Z` (361 rows), `2026-08-06T20:57:23Z` (19 rows), `2026-08-07T04:45:59Z` (27 rows) --
        the PM's query text has no timestamp filter, so 407 is the correct total across all three runs.)

- [x] Step 2: read the real backfill code path. `apply_owner_dispatch_status_corrections.py` is a *different*,
      unrelated script (applies pre-computed `corrected_status` from a prior investigation -- not this sweep).
      The actual writer is **`resource_governor.py`'s `backfill_null_heartbeats()`** (systemd branch, lines
      ~2154-2226), specifically its lookup helper **`_task_yaml_for_umr_row()` (lines 1939-1976)** and the
      terminal fallback at line ~2183. The real rule: for a `status IN ('running','dispatched')`,
      `last_heartbeat IS NULL` row whose bound systemd unit is confirmed inactive
      (`systemctl --user is-active` -> false), it looks for that row's task.yaml two ways -- (1) direct
      `task_docs[task_identity]`, (2) any directory whose name contains `reconcile-umr-<umr_id>` -- and if
      **neither** matches, it unconditionally writes `status='failed'` with reason "no task.yaml found... default
      failed retained". **The actual bug**: `source_trigger='owner_dispatch_gateway'` rows get a synthetic
      `task_identity` (`owner-task-<ts>-<pid>`) that was *never* a real `TASKS_DIR` directory name (the function's
      own docstring says this was confirmed for 261/277 such rows in an earlier cycle) -- the real directory name
      is `outputs_json.new_task_id`, minted by `_perform_spawn()` at actual dispatch time. `_task_yaml_for_umr_row()`
      never checks that field. So the lookup fails, "no evidence" is claimed, and `failed` is written --
      even for the 320 rows that DID produce a real workspace. Confirmed via `resource_governor.py`'s own
      `_forward_progress_decision()` (lines 1979-2056), which is the real, battle-tested, already-reviewed
      evidence-cross-check algorithm this project trusts -- it's just never reached for these 320 because the
      task.yaml lookup feeding it fails first.

- [x] Step 3: re-adjudicated all 320 from real artifacts only (never task.yaml self-report alone -- matches this
      codebase's own stated philosophy, "this task.yaml's own claims are never trusted on their own"). Method
      (script: `evidence/apply_readjudication_320.py`, full per-row trail: `evidence/adjudication_results.json`):
      - Located the real `task.yaml` for each row directly via `outputs_json.new_task_id` (all 320 had one,
        readable; `repo` was `compliance-tracker` for 262, `veridian-scripts` for 58).
      - Fetched **every real PR** (open/closed/merged) in both real repos via `gh api .../pulls` (1018 +
        252 PRs, paginated -- `gh pr list --limit 5000` truncates silently in this environment, do not use it),
        matched by real `head_ref == branch` (branch names are timestamp-unique, so this is an exact, unambiguous
        match, not fuzzy).
      - Computed real commits-ahead-of-`origin/main` for each branch via the shared repo clones (worktrees share
        refs with their parent clone); for the one branch never pushed to origin, fell back to the task's own
        local workspace checkout.
      - Decision: **merged PR -> completed** (verified live: `git merge-base --is-ancestor <merge_sha> origin/main`
        confirmed true for all 68, not just trusted from GitHub's `mergedAt`). **Closed-unmerged PR, or task.yaml
        self-reports a terminal negative (`failed`/`cancelled`/`rejected_duplicate`/`superseded`/`not_needed`) with
        no merged PR -> failed.** **Open PR, or real commits with no PR, or genuinely no PR/no commits at all ->
        requeued** (ambiguous/absent -- no verdict invented).
      - Wrote every correction through **`superboss-register.py`'s own `update_umr_task()` /
        `reset_umr_task_to_queued()` / `validate_umr_terminal_completion_evidence()`**, imported and called
        directly (same convention as `apply_owner_dispatch_status_corrections.py`) -- **never raw SQL**, no new
        tables. `completed` writes required (and got, verified live) a real `--commit-sha` that is a real ancestor
        of `origin/main`. Read-merge-write on `outputs_json`, not a blind replace -- caught and fixed one live
        self-test mistake (`mark-umr-terminal` CLI *does* blind-replace `outputs_json`; the direct-function path
        used for the real 320-row run does not).
      - Duplicate-safety for the 201 `requeued` rows: confirmed **live, before writing**, that all 320
        `task_identity` values are unique in `umr_tasks` (1 row each) and **zero** have any currently
        `queued`/`dispatched`/`running` sibling -- re-checked per-row immediately before each write inside the
        same script. **Residual gap, disclosed, not silently papered over**: `resource_governor.py`'s
        `dispatch_one()` duplicate-PR guard (`_recorded_new_task_ids_for_identity()`) excludes the row's *own*
        `umr_id` when looking for prior `new_task_id` history, so it cannot see *this row's own* prior real
        artifact when the *same* row is later redispatched -- only a genuinely separate sibling row would trip it.
        This is a real dispatcher-side gap, not something a status write can close, and fixing it is out of this
        task's scope (belongs to UMR-20260807-020911-7f31). Of the 201 requeued rows, 145 have a still-open PR and
        41 have real unpushed/unmerged commits -- **PM/owner review before the next dispatch tick is recommended**
        for those 186 to avoid a redundant fresh worker; the other 15 have no artifact at all and are safe to
        redispatch as-is.

- [x] Step 4: applied live. Final counts: **68 completed, 51 failed, 201 requeued** (320 total). Verified
      post-write: all 320 rows moved off `status='failed'`+old backfill reason; all 320 retain their original
      `outputs_json.new_task_id`; the untouched 87 remain `status='failed'`. Corrected trailing-24h
      owner-dispatch-gateway failure rate (recomputed now, same window definition PM used): **17 failed / 237
      submitted = 7.2%** (was PM-reported ~28.8% post-sweep, ~17% pre-sweep -- this number reflects real-time
      state after this remediation, not a re-measurement of the PM's original snapshot instant).

## Remaining

- [ ] None for this task's own scope. Two follow-ups identified but explicitly out of scope, not actioned here:
      1. `_task_yaml_for_umr_row()` in `resource_governor.py` should add a third lookup path via
         `outputs_json.new_task_id`, so this exact mis-adjudication cannot recur on the next backfill/sweep.
      2. The redispatch duplicate-PR guard's self-row-history blind spot (see Step 3 above) should be closed.
      Both are dispatcher-code changes; this task owns only the data re-adjudication, and
      UMR-20260807-020911-7f31 separately owns worker/dispatcher root-cause and reconciliation -- not duplicated
      here.
