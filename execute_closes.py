#!/usr/bin/env python3
import yaml
import subprocess
import sys
import json
from collections import defaultdict
from datetime import datetime

def load_master_list():
    with open('master_list.yaml', 'r') as f:
        return yaml.safe_load(f)

def parse_pr_id(pr_id):
    parts = pr_id.split('#')
    if len(parts) != 2:
        return None, None
    return parts[0], parts[1]

def map_repo_to_github(repo_base):
    mapping = {
        'claude-control': 'FChecklist/claude-control',
        'compliance-tracker': 'FChecklist/compliance-tracker',
        'projexa': 'FChecklist/projexa',
        'veridian-scripts': 'FChecklist/veridian-scripts',
        'veridian-ai-os': 'FChecklist/veridian-ai-os'
    }
    return mapping.get(repo_base, f'FChecklist/{repo_base}')

def close_pr_via_gh(repo, pr_num, comment):
    cmd = ['gh', 'pr', 'close', pr_num, '--repo', repo, '--comment', comment]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, '', str(e)

master_list = load_master_list()
close_items = [item for item in master_list['items'] if item['recommended_action'] == 'CLOSE']

# Group by evidence
evidence_groups = defaultdict(list)
for item in close_items:
    evidence = item.get('evidence', 'unknown')
    evidence_groups[evidence].append(item)

print(f"Processing {len(close_items)} CLOSE items in batches...\n")

closed_log = []
failed_log = []
execution_log = []

# Process docs-only batch (222 items)
docs_only = evidence_groups.get("Open PR contains only markdown/progress files, no real code changes", [])
print(f"Batch 1: Docs-only ({len(docs_only)} items)")

for i, item in enumerate(docs_only):
    repo_base, pr_num = parse_pr_id(item['id'])
    if not repo_base:
        failed_log.append((item['id'], "Parse error"))
        execution_log.append({
            'item_id': item['id'],
            'status': 'FAILED',
            'reason': 'Parse error',
            'timestamp': datetime.utcnow().isoformat()
        })
        continue

    repo = map_repo_to_github(repo_base)
    comment = f"""This PR is being closed as it contains only documentation and progress updates, with no real code changes.

**Evidence:** {item['evidence']}
**Reference:** task-20260817-132903-close-every-item-on-the-master-pendency
"""

    success, stdout, stderr = close_pr_via_gh(repo, pr_num, comment)
    if success:
        closed_log.append(item['id'])
        execution_log.append({
            'item_id': item['id'],
            'status': 'CLOSED',
            'repo': repo,
            'pr_num': pr_num,
            'timestamp': datetime.utcnow().isoformat()
        })
        if (i+1) % 20 == 0:
            print(f"  Progress: {i+1}/{len(docs_only)} closed")
    else:
        failed_log.append((item['id'], stderr[:100] if stderr else "Unknown error"))
        execution_log.append({
            'item_id': item['id'],
            'status': 'FAILED',
            'repo': repo,
            'pr_num': pr_num,
            'error': stderr[:200] if stderr else "Unknown error",
            'timestamp': datetime.utcnow().isoformat()
        })

print(f"  Batch 1 complete: {len(closed_log)} closed, {len(failed_log)} failed\n")

# Process remaining duplicates in smaller batches
print(f"Batch 2: Duplicates ({len(close_items) - len(docs_only)} items)")
dup_count = 0

for evidence, items in sorted(evidence_groups.items(), key=lambda x: -len(x[1]))[1:]:
    if "Duplicate of" not in evidence:
        continue

    for item in items:
        repo_base, pr_num = parse_pr_id(item['id'])
        if not repo_base:
            failed_log.append((item['id'], "Parse error"))
            continue

        repo = map_repo_to_github(repo_base)
        comment = f"""This PR is being closed as a duplicate.

**Evidence:** {item['evidence']}
**Reference:** task-20260817-132903-close-every-item-on-the-master-pendency
"""

        success, stdout, stderr = close_pr_via_gh(repo, pr_num, comment)
        dup_count += 1
        if success:
            closed_log.append(item['id'])
            execution_log.append({
                'item_id': item['id'],
                'status': 'CLOSED',
                'repo': repo,
                'pr_num': pr_num,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            failed_log.append((item['id'], stderr[:100] if stderr else "Unknown error"))
            execution_log.append({
                'item_id': item['id'],
                'status': 'FAILED',
                'error': stderr[:200] if stderr else "Unknown error",
                'timestamp': datetime.utcnow().isoformat()
            })

        if dup_count % 20 == 0:
            print(f"  Progress: {dup_count}/{len(close_items) - len(docs_only)} duplicates processed")

print(f"  Batch 2 complete: processed {dup_count} duplicates\n")

# Summary
print(f"\n{'='*70}")
print(f"CLOSE Actions Summary:")
print(f"  Total to close: {len(close_items)}")
print(f"  Successfully closed: {len(closed_log)}")
print(f"  Failed: {len(failed_log)}")

if failed_log:
    print(f"\nFailed items (first 10):")
    for item_id, reason in failed_log[:10]:
        print(f"  - {item_id}: {reason}")
    if len(failed_log) > 10:
        print(f"  ... and {len(failed_log) - 10} more")

# Save execution log
with open('close_execution_log.json', 'w') as f:
    json.dump({
        'timestamp': datetime.utcnow().isoformat(),
        'total_processed': len(close_items),
        'successful': len(closed_log),
        'failed': len(failed_log),
        'executions': execution_log
    }, f, indent=2)

print(f"\nExecution log saved to close_execution_log.json")
