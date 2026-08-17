#!/usr/bin/env python3
import json
import re

results = json.load(open("match_results_corrected.json"))

def clean_snippet(s):
    s = re.sub(r'\s+', ' ', s or '').strip()
    if len(s) > 220:
        s = s[:217] + "..."
    return s

items_out = []
n_direct = 0
n_plausible = 0
n_none = 0
by_action_total = {}
by_action_covered = {}

for r in results:
    it = r["item"]
    action = it["recommended_action"]
    by_action_total[action] = by_action_total.get(action, 0) + 1

    direct = r["direct"]
    plausible = r["plausible"]

    if direct:
        n_direct += 1
        by_action_covered[action] = by_action_covered.get(action, 0) + 1
        primary = direct[0]
        others = direct[1:] + plausible
        reasoning = (
            f"Direct match: real task {primary['id']} names {r['repo_short']}#{r['pr_num']} "
            f"in its own prompt/progress text -- evidence: \"{clean_snippet(primary['snippet'])}\""
        )
        entry = {
            "item_id": it["id"],
            "item_title": it["title"],
            "repo": it["repo"],
            "recommended_action": action,
            "pendency_classification": it["classification"],
            "coverage_exists": True,
            "confidence": "direct",
            "matching_task_id": primary["id"][:46],
            "matching_task_full_id": primary["id"],
            "matching_task_status": primary["status_live"],
            "other_matching_tasks": [
                {"task_id": o["id"][:46], "task_full_id": o["id"], "status": o["status_live"]} for o in others
            ],
            "reasoning": reasoning,
        }
    elif plausible:
        n_plausible += 1
        by_action_covered[action] = by_action_covered.get(action, 0) + 1
        primary = plausible[0]
        others = plausible[1:]
        reasoning = (
            f"Plausible match: real task {primary['id']} mentions both {r['repo_short']} and "
            f"PR/#{r['pr_num']} in the same prompt/progress text but not tightly co-located -- "
            f"evidence: \"{clean_snippet(primary['snippet'])}\" (needs human confirmation that this "
            f"is the same feature, not just a nearby PR-number mention)"
        )
        entry = {
            "item_id": it["id"],
            "item_title": it["title"],
            "repo": it["repo"],
            "recommended_action": action,
            "pendency_classification": it["classification"],
            "coverage_exists": True,
            "confidence": "plausible",
            "matching_task_id": primary["id"][:46],
            "matching_task_full_id": primary["id"],
            "matching_task_status": primary["status_live"],
            "other_matching_tasks": [
                {"task_id": o["id"][:46], "task_full_id": o["id"], "status": o["status_live"]} for o in others
            ],
            "reasoning": reasoning,
        }
    else:
        n_none += 1
        by_action_covered.setdefault(action, by_action_covered.get(action, 0))
        entry = {
            "item_id": it["id"],
            "item_title": it["title"],
            "repo": it["repo"],
            "recommended_action": action,
            "pendency_classification": it["classification"],
            "coverage_exists": False,
            "confidence": None,
            "matching_task_id": None,
            "matching_task_status": None,
            "other_matching_tasks": [],
            "reasoning": (
                f"No real post-dispatch task found whose own prompt.txt or progress record names "
                f"{r['repo_short']}#{r['pr_num']} (searched all {2216} real queue-manager.py-listed "
                f"post-dispatch tasks' own prompt/progress text for repo+PR-number co-occurrence and "
                f"explicit GitHub PR URLs; none matched)."
            ),
        }
    items_out.append(entry)

summary = {
    "total_items": len(items_out),
    "source_master_list": {
        "path": "task-20260817-141839-fix-fabricated-pendency-list-self-audit/workspace/master_list.json",
        "note": (
            "A corrected master pendency list landed from the ground-truth-verification remediation "
            "(task-20260817-141839) during this task's run and was used in place of the original "
            "task-20260817-130826/workspace/master_list.json. The original's own AUDIT_VERIFICATION.md "
            "was a fabricated self-audit (its own PR #16 was rejected by review for exactly this reason); "
            "its ENUMERATION_REPORT.md honestly admitted only 400/711 items (56%) were ground-truth "
            "verified. task-20260817-141839 independently re-ran ground-truth verification for all "
            "711/711 items (real gh CLI file-change + audit-verdict-comment queries, not carried over), "
            "fixed a deduplication bug that had falsely grouped 56 unrelated items as duplicates, and "
            "produced this corrected master_list.json with a real, independently-resolvable head commit "
            "(07c469b3723cb04cd152e0e72e50e5230b40b47e). "
            "CAVEAT: task-20260817-141839 itself is still status=blocked (not yet merged to main) as of "
            "when this coverage map was built -- its output is the best real evidence available, not yet "
            "the permanent canonical list. If it is later superseded again, this coverage map should be "
            "regenerated against whatever list is canonical at that time."
        ),
        "total_merge_revise_implement_items": 425,
        "note_on_count_change": (
            "The task's own name/spec anticipated 411 items (123 MERGE + 23 REVISE + 265 IMPLEMENT) from "
            "the original, since-superseded list. The corrected list has 425 (130 MERGE + 25 REVISE + "
            "270 IMPLEMENT) -- 14 more, because 56 items previously mis-classified as DUPLICATE_OF (and "
            "thus recommended CLOSE) were correctly reclassified as REAL_CODE_UNMERGED/GENUINELY_OPEN_"
            "UNSTARTED after the dedup-bug fix, and some items' live-state drift also shifted counts. "
            "Every one of these 425 corrected-list items appears exactly once below."
        ),
    },
    "matching_task_id_note": (
        "queue-manager.py list truncates the ID column to 46 characters for display "
        "(source: t['id'][:46] in queue-manager.py). matching_task_id in each item below is that "
        "same 46-char-truncated form, so it is guaranteed to be a literal substring of a real line in "
        "`python3 /opt/veridian/scripts/queue-manager.py list` output. matching_task_full_id carries the "
        "complete, untruncated real task directory id for humans/scripts that need it."
    ),
    "search_method": (
        "Every one of the 2216 real post-dispatch tasks currently listed by "
        "`python3 /opt/veridian/scripts/queue-manager.py list` was indexed on its own real prompt.txt "
        "plus its own real progress record (workspace/PROGRESS.md and, where present, the correctly-"
        "attributed progress/<that-task's-own-id>.md -- NOT whatever other tasks' progress files "
        "happened to be physically copied into a given task's workspace by the workspace-priming step, "
        "which was found to cross-contaminate a naive per-directory read). For each of the 425 items, "
        "matches were found via (a) an explicit github.com/<repo>/pull/<num> URL, or (b) the item's repo "
        "short name and PR number appearing within 30 characters of each other in that task's own real "
        "text (direct/strong), or within 150 characters (plausible/weak). Matches from this task chain's "
        "own meta/process tasks (enumerate, close-every-item, certify-or-refuse, fix-fabricated-audit, "
        "and this task itself) were excluded from counting as coverage, since they are about the pendency "
        "list process itself, not real dispatched work on an individual item. A prior looser matching pass "
        "(whole-blob co-occurrence, and trusting truncated task-directory names as PR numbers) was tried "
        "and discarded after producing verified false positives (e.g. a directory name truncated to "
        "'...-rebasing-pr-75' was actually about PR 754/757/758, not PR 75); see PROGRESS.md for detail."
    ),
    "counts": {
        "with_coverage": n_direct + n_plausible,
        "with_direct_match": n_direct,
        "with_plausible_match_only": n_plausible,
        "no_coverage_found": n_none,
    },
    "by_recommended_action": {
        action: {
            "total": by_action_total[action],
            "with_coverage": by_action_covered.get(action, 0),
            "no_coverage": by_action_total[action] - by_action_covered.get(action, 0),
        }
        for action in sorted(by_action_total)
    },
}

out = {"summary": summary, "items": items_out}
with open("coverage_map.json", "w") as f:
    json.dump(out, f, indent=2)

print(json.dumps(summary, indent=2))
print("items written:", len(items_out))
