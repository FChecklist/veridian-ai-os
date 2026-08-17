# Coverage map pipeline (task-20260817-141859)

`coverage_map.json` is the deliverable. It was produced by running these
scripts in order (intermediate artifacts were deleted after use -- they are
large, fully regeneratable, and add nothing once `coverage_map.json` exists;
rerun this sequence to reproduce them):

1. `python3 /opt/veridian/scripts/queue-manager.py list > queue_list_raw.txt`
2. `python3 parse_queue.py` -> `queue_status_map.json`
   (real post-dispatch task id -> real current status, keyed by the same
   46-char id truncation `queue-manager.py list` itself displays)
3. `python3 build_progress_corpus.py` -> `progress_corpus.json`
   (deduped, per-task-id-attributed real progress/<task-id>.md content --
   see note below on why this correction was necessary)
4. `python3 build_index2.py` -> `task_index2.json`
   (one real text blob per post-dispatch task: title + its own real
   prompt.txt + its own real workspace/PROGRESS.md + its own real
   progress-corpus entry)
5. `python3 build_reverse_index_final.py` -> `strong_index_final.json`,
   `weak_index_final.json`, `snippet_index_final.json`
   (repo+PR-number -> matching real tasks, direct vs plausible, see
   confidence-tier definition below)
6. `python3 extract_items_corrected.py` -> `target_items_corrected.json`
   (the 425 MERGE/REVISE/IMPLEMENT items from the corrected master list)
7. `python3 match_final.py` -> `match_results_corrected.json`
8. `python3 generate_coverage_map.py` -> `coverage_map.json`
9. `python3 verify_map.py` -- sanity checks (all matching_task_id values are
   real, literally present in queue-manager.py's real list output; 425
   unique item ids)

## Source master list

Used `task-20260817-141839-fix-fabricated-pendency-list-self-audit/workspace/master_list.json`
(the corrected, independently re-verified list -- 711/711 ground-truth
items, real resolvable head commit `07c469b3723cb04cd152e0e72e50e5230b40b47e`),
NOT the original `task-20260817-130826/workspace/master_list.json` (its own
`AUDIT_VERIFICATION.md` was a fabricated self-audit; its own
`ENUMERATION_REPORT.md` honestly admitted only 56% ground-truth completion;
its PR #16 was rejected by review for exactly this reason). See
`coverage_map.json`'s own `summary.source_master_list` field for the full
citation and caveats (including that task-20260817-141839 was itself still
`status: blocked`, not yet merged to main, when this map was built).

## Confidence tiers

- **direct**: the matching task's own real prompt.txt/progress text either
  (a) contains an explicit `github.com/<owner>/<repo>/pull/<num>` URL for
  the exact item, or (b) names the repo short-name and the PR number within
  30 characters of each other.
- **plausible**: repo short-name and PR number both appear in the matching
  task's own real text, within 150 characters of each other but not within
  30 -- worth a human's second look, not a confident claim.
- **no coverage**: no repo+PR-number co-occurrence found anywhere in any of
  the 2216 real post-dispatch tasks' own real text.

## Corrections made mid-pipeline (kept here so the method is auditable)

1. **Task-directory names are truncated** by the task-creation system at a
   fixed length. An early version of this pipeline extracted PR numbers
   from directory names (e.g. `...-rebasing-pr-75`) and got it wrong: that
   directory's real content was about PR 754/757/758, not PR 75 -- the
   dirname was simply cut off mid-number. Dirname-based PR-number extraction
   was dropped entirely; only real prompt/progress *text* is trusted.
2. **`workspace/progress/*.md` is not unique to the containing task.** A
   workspace-priming/resync step was found to copy many *other* tasks' real
   `progress/<their-id>.md` files into a new task's own workspace. Reading
   whichever files happened to be physically present and attributing them
   to the containing task directory produced clearly wrong matches (e.g.
   attributing a different task's real DDL-gate fix to an unrelated
   "audit and land the remaining PRs" task that had never actually started).
   `build_progress_corpus.py` fixes this by scanning every task's
   `workspace/progress/*.md`, keying content by the **task id named in the
   filename** (not the containing directory), and deduping to the longest
   version of each. `build_index2.py` then looks up each task's *own*
   progress content by its own id from that corrected corpus.
3. **Whole-blob co-occurrence was too loose.** An even earlier pass counted
   a match whenever a repo name and a PR-like number both appeared anywhere
   in a ~40KB blob, with no proximity requirement -- this produced ~300/411
   "matches", almost all spurious (e.g. a single long unwrapped prompt
   sentence mentioning `compliance-tracker PR #74` and, 200 characters
   later in the same line, an unrelated `repos/claude-control/` path,
   wrongly paired as `claude-control#74`). Replaced with the
   character-proximity windows described above.

This task did not create, dispatch, merge, close, or revise any task or
pull request -- it only read the real task queue and the real master
pendency list, and wrote `coverage_map.json`.
