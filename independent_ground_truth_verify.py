#!/usr/bin/env python3
"""
Independent ground-truth re-verification for task-20260817-130826's
711-item pendency enumeration.

This script is authored and run by task-20260817-141839, a process
distinct from the worker that produced the original (partial, 56%)
verification and the fabricated self-audit. It re-runs real `gh` CLI
queries against GitHub for every one of the 711 enumerated items --
none of the prior verified_enumeration.json data is copied in without
being independently re-confirmed here.

Method (same evidence basis as the original task's verify_ground_truth.py,
per spec instruction to reuse the method, not the unverified output):
  - For type == 'pr': `gh pr view <num> --repo <repo> --json state,files,comments,mergedAt`
      - has_real_code: True if any changed file is outside the
        markdown/progress/txt/yaml/notes exclusion set (same rule as the
        original script).
      - audit_verdict: first "AUDIT: PASS" / "AUDIT: FAIL" literal found
        in PR comment bodies (same rule as the original script).
      - ground_truth_status: MARKDOWN_ONLY / AUDIT_FAILED / REAL_CODE / UNVERIFIABLE
      - live_state captured too, to detect drift since the original
        13:22 snapshot (PRs can close/merge between runs).
  - For type == 'followup': these are NOT distinct closeable PRs -- they
    are synthetic tracking rows this task's enumeration step derived
    from unchecked-checklist text inside an ALREADY-MERGED, DIFFERENT PR.
    "Verifying" one means confirming the parent PR that the text was
    extracted from is real and actually merged (i.e. the construct is
    grounded in a real artifact, not invented). We do that via
    `gh pr view <parent_num> --repo <repo> --json state,mergedAt`.
    ground_truth_status stays FOLLOWUP_ITEM, matching the original method.

Output: ground_truth_reconfirmed.json in this task's own workspace.
"""
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

SOURCE_RAW = '/opt/veridian/ai-os/tasks/task-20260817-130826-enumerate-and-deduplicate-all-pendency-s/workspace/raw_enumeration.json'
OUT_PATH = '/opt/veridian/ai-os/tasks/task-20260817-141839-fix-fabricated-pendency-list-self-audit/workspace/ground_truth_reconfirmed.json'

EXCLUDE_PATTERNS = [
    r'\.md$',
    r'progress/',
    r'PROGRESS\.md',
    r'\.txt$',
    r'\.yaml$',
    r'notes/',
]


def has_real_code_changes(files):
    if not files:
        return None
    real_files = []
    for f in files:
        path = f.get('path', '')
        if not any(re.search(p, path) for p in EXCLUDE_PATTERNS):
            real_files.append(path)
    return len(real_files) > 0


def find_audit_verdict(comments):
    if not comments:
        return None
    for c in comments:
        body = c.get('body', '')
        if 'AUDIT: PASS' in body:
            return 'PASS'
        if 'AUDIT: FAIL' in body:
            return 'FAIL'
    return None


def gh_json(args, timeout=20, retries=2):
    for attempt in range(retries + 1):
        try:
            result = subprocess.run(
                ['gh'] + args,
                capture_output=True, text=True, timeout=timeout
            )
            if result.returncode == 0:
                return json.loads(result.stdout), None
            else:
                last_err = result.stderr.strip()[:300]
        except Exception as e:
            last_err = str(e)[:300]
        time.sleep(0.5)
    return None, last_err


def verify_pr_item(row):
    item_id = row['item_id']
    repo = row['repo']
    m = re.search(r'#(\d+)', item_id)
    if not m:
        row['ground_truth_status'] = 'UNVERIFIABLE'
        row['verify_error'] = 'could not parse PR number from item_id'
        return row
    pr_num = int(m.group(1))

    data, err = gh_json(['pr', 'view', str(pr_num), '--repo', repo,
                          '--json', 'state,files,comments,mergedAt'])
    if data is None:
        row['ground_truth_status'] = 'UNVERIFIABLE'
        row['verify_error'] = err
        return row

    files = data.get('files', [])
    comments = data.get('comments', [])
    live_state = data.get('state')

    row['_files_count'] = len(files)
    row['_files_sample'] = [f.get('path') for f in files[:15]]
    row['has_real_code'] = has_real_code_changes(files)
    row['audit_verdict'] = find_audit_verdict(comments)
    row['live_state'] = live_state
    row['live_merged_at'] = data.get('mergedAt')
    row['state_drift'] = (live_state != 'OPEN') if row.get('status') == 'open' else False

    if row['has_real_code'] is None:
        row['ground_truth_status'] = 'UNVERIFIABLE'
    elif not row['has_real_code']:
        row['ground_truth_status'] = 'MARKDOWN_ONLY'
    elif row['audit_verdict'] == 'FAIL':
        row['ground_truth_status'] = 'AUDIT_FAILED'
    else:
        row['ground_truth_status'] = 'REAL_CODE'
    row['verify_error'] = None
    return row


def verify_followup_item(row):
    item_id = row['item_id']
    repo = row['repo']
    m = re.search(r'#(\d+)-followup', item_id)
    row['ground_truth_status'] = 'FOLLOWUP_ITEM'
    row['is_synthetic_construct'] = True
    row['closing_action_note'] = (
        "This id does not name a distinct open pull request; it is a "
        "tracking row this enumeration derived from unchecked follow-up "
        "text inside an already-merged PR. There is no PR object to "
        "`gh pr close`. A recommended_action of CLOSE on this row means: "
        "mark the follow-up text resolved/withdrawn (e.g. edit the parent "
        "PR's checklist or the tracking doc it came from), not an API "
        "close call. A recommended_action of IMPLEMENT means the "
        "described work still needs a real PR opened against it."
    )
    if not m:
        row['verify_error'] = 'could not parse parent PR number from item_id'
        row['parent_pr_state'] = None
        return row
    parent_num = int(m.group(1))
    data, err = gh_json(['pr', 'view', str(parent_num), '--repo', repo,
                          '--json', 'state,mergedAt,title'])
    if data is None:
        row['parent_pr_state'] = None
        row['verify_error'] = err
    else:
        row['parent_pr_state'] = data.get('state')
        row['parent_pr_merged_at'] = data.get('mergedAt')
        row['parent_pr_confirmed_merged'] = data.get('state') == 'MERGED'
        row['verify_error'] = None
    return row


def verify_one(row):
    if row['item_type'] == 'pr':
        return verify_pr_item(row)
    else:
        return verify_followup_item(row)


def main():
    with open(SOURCE_RAW) as f:
        rows = json.load(f)
    print(f"Loaded {len(rows)} raw items from task-20260817-130826 enumeration (read-only source).")

    results = [None] * len(rows)
    done = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(verify_one, dict(row)): i for i, row in enumerate(rows)}
        for fut in as_completed(futs):
            i = futs[fut]
            results[i] = fut.result()
            done += 1
            if done % 50 == 0 or done == len(rows):
                print(f"  Progress: {done}/{len(rows)}", file=sys.stderr)

    with open(OUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    stats = {}
    errs = 0
    for r in results:
        stats[r['ground_truth_status']] = stats.get(r['ground_truth_status'], 0) + 1
        if r.get('verify_error'):
            errs += 1
    print("\nIndependent re-verification complete.")
    print(json.dumps(stats, indent=2))
    print(f"Items with verify errors (unverifiable via live gh call): {errs}")
    print(f"Total: {len(results)}")
    print(f"Saved to {OUT_PATH}")


if __name__ == '__main__':
    main()
