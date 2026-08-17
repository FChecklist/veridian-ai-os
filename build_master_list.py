#!/usr/bin/env python3
"""
Regenerate the master pendency list from real, independently re-confirmed
data only (task-20260817-141839, distinct from task-20260817-130826's
own worker process).

Inputs (all produced or independently re-verified by this task):
  - ground_truth_reconfirmed.json  : fresh `gh` CLI evidence for all 711 items
  - duplicate_groups_reconfirmed.json : corrected dedup pass (fixes a
    confirmed false-positive bug in the reused conservative dedup script)

Schema and category/action vocabulary are reused verbatim from the
existing (pre-this-task) master_list.json -- no new categories invented,
per task spec instruction.
"""
import json
from datetime import datetime

GT_PATH = '/opt/veridian/ai-os/tasks/task-20260817-141839-fix-fabricated-pendency-list-self-audit/workspace/ground_truth_reconfirmed.json'
DUPES_PATH = '/opt/veridian/ai-os/tasks/task-20260817-141839-fix-fabricated-pendency-list-self-audit/workspace/duplicate_groups_reconfirmed.json'
OUT_JSON = '/opt/veridian/ai-os/tasks/task-20260817-141839-fix-fabricated-pendency-list-self-audit/workspace/master_list.json'
OUT_YAML = '/opt/veridian/ai-os/tasks/task-20260817-141839-fix-fabricated-pendency-list-self-audit/workspace/master_list.yaml'

FOLLOWUP_CLOSE_NOTE = (
    " NOTE: this id is not a distinct open pull request -- it is a "
    "tracking row this enumeration derived from unchecked follow-up text "
    "inside an already-merged, different PR. There is no PR object to "
    "`gh pr close`; CLOSE here means marking the follow-up text "
    "resolved/withdrawn wherever it is tracked (e.g. the parent PR's "
    "checklist), not an API close call."
)


def load():
    with open(GT_PATH) as f:
        gt = json.load(f)
    with open(DUPES_PATH) as f:
        dupes = json.load(f)
    return gt, dupes


def build_duplicate_map(dupes):
    """non-canonical item_id -> canonical item_id"""
    m = {}
    for g in dupes['details']:
        canonical = g['member_ids'][0]
        for mid in g['member_ids'][1:]:
            m[mid] = canonical
    return m


def classify(row, dup_of):
    item_id = row['item_id']
    item_type = row['item_type']

    if item_id in dup_of:
        canonical = dup_of[item_id]
        evidence = (
            f"Duplicate of {canonical} (title similarity >0.90 or a "
            f"duplicate/supersede/replace/revert/undo keyword within 30 "
            f"chars of {canonical}'s PR number in this item's title, or "
            f"vice versa -- re-derived independently by task-20260817-141839, "
            f"see duplicate_groups_reconfirmed.json)."
        )
        if item_type == 'followup':
            evidence += FOLLOWUP_CLOSE_NOTE
        return {
            'classification': 'DUPLICATE_OF',
            'evidence': evidence,
            'recommended_action': 'CLOSE',
        }

    if item_type == 'followup':
        parent_ok = row.get('parent_pr_confirmed_merged')
        evidence = (
            "Follow-up work declared in an already-merged PR; independently "
            f"reconfirmed the parent PR (state={row.get('parent_pr_state')}) "
            f"via live gh CLI query -- {'confirmed merged' if parent_ok else 'NOT confirmed merged, see verify_error'}."
        )
        evidence += FOLLOWUP_CLOSE_NOTE.replace(
            "CLOSE here means", "If ever marked CLOSE, that means"
        )
        return {
            'classification': 'GENUINELY_OPEN_UNSTARTED',
            'evidence': evidence,
            'recommended_action': 'IMPLEMENT',
        }

    # item_type == 'pr'
    gts = row.get('ground_truth_status')
    live_state = row.get('live_state')
    drift_note = ''
    if row.get('state_drift'):
        drift_note = f" (live state has drifted to {live_state} since original enumeration snapshot recorded status=open)"

    if gts == 'MARKDOWN_ONLY':
        return {
            'classification': 'DOCS_ONLY_NO_CODE',
            'evidence': f"Live gh CLI file-change check: all changed files are markdown/progress/txt/yaml/notes, no real code.{drift_note}",
            'recommended_action': 'CLOSE',
        }
    if gts == 'AUDIT_FAILED':
        return {
            'classification': 'BLOCKED_ON_AUDIT',
            'evidence': f"Live gh CLI check: real code changes present, but PR comments contain an explicit AUDIT: FAIL verdict.{drift_note}",
            'recommended_action': 'REVISE',
        }
    if gts == 'REAL_CODE':
        return {
            'classification': 'REAL_CODE_UNMERGED',
            'evidence': f"Live gh CLI file-change check: real code changes present, no AUDIT: FAIL verdict found in comments.{drift_note}",
            'recommended_action': 'MERGE',
        }
    return {
        'classification': 'UNVERIFIABLE',
        'evidence': f"gh CLI query did not return usable file/comment data: {row.get('verify_error')}",
        'recommended_action': 'ESCALATE',
    }


def main():
    gt, dupes = load()
    dup_of = build_duplicate_map(dupes)

    master_rows = []
    for row in gt:
        c = classify(row, dup_of)
        status = row.get('live_state', row.get('status', 'unknown'))
        if row['item_type'] == 'followup':
            status = row.get('status', 'merged_with_undone_work')
        else:
            status = (status or 'unknown').lower()
        master_rows.append({
            'id': row['item_id'],
            'type': row['item_type'],
            'repo': row['repo'],
            'title': row['title'],
            'classification': c['classification'],
            'evidence': c['evidence'],
            'recommended_action': c['recommended_action'],
            'status': status,
            'created_date': row.get('created_date', ''),
            'link': row.get('link', ''),
        })

    action_order = {'CLOSE': 0, 'MERGE': 1, 'REVISE': 2, 'IMPLEMENT': 3, 'ESCALATE': 4}

    def sort_key(r):
        return (action_order.get(r['recommended_action'], 99), r['repo'], r['created_date'])

    sorted_rows = sorted(master_rows, key=sort_key)

    classification_stats = {}
    action_stats = {}
    for r in master_rows:
        classification_stats[r['classification']] = classification_stats.get(r['classification'], 0) + 1
        action_stats[r['recommended_action']] = action_stats.get(r['recommended_action'], 0) + 1

    master_list = {
        'metadata': {
            'generated_at': '2026-08-17T15:00:00',
            'generated_by': 'task-20260817-141839-fix-fabricated-pendency-list-self-audit (independent re-verification, not the original task-20260817-130826 worker process)',
            'total_items': len(master_rows),
            'duplicate_items': sum(1 for r in master_rows if r['classification'] == 'DUPLICATE_OF'),
            'surviving_items': len([r for r in master_rows if r['classification'] != 'DUPLICATE_OF']),
            'window_start': '2026-07-15',
            'window_end': '2026-08-17',
            'ground_truth_completion_pct': 100.0,
            'ground_truth_method': 'gh CLI file-change + PR-comment audit-verdict queries, all 711 items, run by independent_ground_truth_verify.py',
            'supersedes': [
                'task-20260817-130826 workspace: master_list.json, master_list.yaml, ENUMERATION_REPORT.md, AUDIT_VERIFICATION.md, classified_enumeration.json, duplicate_groups_conservative.json (all left in place, unmodified -- this task has no write access to that workspace; see VERIFICATION_REPORT for why each is superseded)',
            ],
        },
        'statistics': {
            'by_classification': classification_stats,
            'by_recommended_action': action_stats,
        },
        'items': sorted_rows,
    }

    with open(OUT_JSON, 'w') as f:
        json.dump(master_list, f, indent=2)

    try:
        import yaml
        with open(OUT_YAML, 'w') as f:
            yaml.dump(master_list, f, default_flow_style=False, sort_keys=False)
    except ImportError:
        print("pyyaml not available, skipping YAML output")

    print("Classification:", json.dumps(classification_stats, indent=2))
    print("Actions:", json.dumps(action_stats, indent=2))
    print("Total:", len(master_rows))


if __name__ == '__main__':
    main()
