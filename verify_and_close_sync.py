#!/usr/bin/env python3
"""
Synchronous PR close execution for task-20260817-134841.
Verifies current state, closes in batches, verifies after each batch.
"""

import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime

def load_master_list():
    """Load the master list of items to close."""
    with open('master_list.json', 'r') as f:
        return json.load(f)

def parse_pr_id(pr_id):
    """Parse PR ID like 'compliance-tracker#558' into (repo_base, repo_num)."""
    parts = pr_id.split('#')
    if len(parts) != 2:
        return None, None
    return parts[0], parts[1]

def map_repo_to_github(repo_base):
    """Map repo base name to GitHub org/repo."""
    mapping = {
        'claude-control': 'FChecklist/claude-control',
        'compliance-tracker': 'FChecklist/compliance-tracker',
        'projexa': 'FChecklist/projexa',
        'veridian-scripts': 'FChecklist/veridian-scripts',
        'veridian-ai-os': 'FChecklist/veridian-ai-os'
    }
    return mapping.get(repo_base, f'FChecklist/{repo_base}')

def get_pr_state(repo, pr_num):
    """Check if a PR is open or closed via gh CLI."""
    cmd = ['gh', 'pr', 'view', pr_num, '--repo', repo, '--json', 'state']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get('state')  # 'OPEN' or 'CLOSED'
        return None
    except Exception as e:
        print(f"  Error checking {repo}#{pr_num}: {e}", file=sys.stderr)
        return None

def close_pr_via_gh(repo, pr_num, comment):
    """Close a PR using gh CLI, synchronously."""
    cmd = ['gh', 'pr', 'close', pr_num, '--repo', repo, '--comment', comment]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, '', str(e)

def write_progress_log(log_entries, filename='close_progress_log.jsonl'):
    """Append entries to an incremental progress log."""
    with open(filename, 'a') as f:
        for entry in log_entries:
            f.write(json.dumps(entry) + '\n')

def read_progress_log(filename='close_progress_log.jsonl'):
    """Read existing progress log."""
    try:
        with open(filename, 'r') as f:
            return [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        return []

def main():
    master_list = load_master_list()
    close_items = [item for item in master_list.get('items', [])
                   if item.get('recommended_action') == 'CLOSE']

    print(f"Task: task-20260817-134841 - Close master pendency items (synchronously)")
    print(f"Total CLOSE items in master list: {len(close_items)}")
    print()

    # Group by evidence
    evidence_groups = defaultdict(list)
    for item in close_items:
        evidence = item.get('evidence', 'unknown')
        evidence_groups[evidence].append(item)

    # Read existing progress
    progress_log = read_progress_log()
    already_processed = {entry['item_id'] for entry in progress_log if entry['status'] in ['CLOSED', 'FAILED', 'SKIPPED']}
    print(f"Already processed (from log): {len(already_processed)}")

    # Get remaining items
    remaining = [item for item in close_items if item['id'] not in already_processed]
    print(f"Remaining to process: {len(remaining)}")
    print()

    if not remaining:
        print("All items already processed! No work to do.")
        return

    # STEP 1: Verify current state of all remaining items
    print("="*70)
    print("STEP 1: Verifying current PR state...")
    print("="*70)

    verification_results = {}
    for item in remaining:
        repo_base, pr_num = parse_pr_id(item['id'])
        if not repo_base:
            verification_results[item['id']] = {'status': 'PARSE_ERROR'}
            continue

        repo = map_repo_to_github(repo_base)
        state = get_pr_state(repo, pr_num)
        verification_results[item['id']] = {'state': state, 'repo': repo, 'pr_num': pr_num}

    # Categorize verification results
    open_prs = []
    closed_prs = []
    unreachable_prs = []
    parse_errors = []

    for item in remaining:
        result = verification_results[item['id']]
        if result.get('status') == 'PARSE_ERROR':
            parse_errors.append(item)
        elif result.get('state') == 'OPEN':
            open_prs.append(item)
        elif result.get('state') == 'CLOSED':
            closed_prs.append(item)
        else:
            unreachable_prs.append(item)

    print(f"  OPEN (need closing): {len(open_prs)}")
    print(f"  CLOSED (already closed): {len(closed_prs)}")
    print(f"  UNREACHABLE/ERROR (could not verify): {len(unreachable_prs)}")
    print(f"  PARSE_ERROR: {len(parse_errors)}")
    print()

    # Log already-closed items and errors
    progress_updates = []
    for item in closed_prs:
        progress_updates.append({
            'item_id': item['id'],
            'status': 'SKIPPED',
            'reason': 'Already closed',
            'timestamp': datetime.utcnow().isoformat()
        })

    for item in unreachable_prs:
        progress_updates.append({
            'item_id': item['id'],
            'status': 'SKIPPED',
            'reason': 'Could not verify state',
            'timestamp': datetime.utcnow().isoformat()
        })

    for item in parse_errors:
        progress_updates.append({
            'item_id': item['id'],
            'status': 'FAILED',
            'reason': 'Parse error',
            'timestamp': datetime.utcnow().isoformat()
        })

    if progress_updates:
        write_progress_log(progress_updates)

    # STEP 2: Close items in batches
    print("="*70)
    print("STEP 2: Closing items in batches (synchronously)...")
    print("="*70)
    print()

    batch_size = 25
    total_batches = (len(open_prs) + batch_size - 1) // batch_size

    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min((batch_num + 1) * batch_size, len(open_prs))
        batch = open_prs[start_idx:end_idx]

        print(f"Batch {batch_num + 1}/{total_batches}: Closing {len(batch)} items...")

        batch_progress = []
        closed_in_batch = 0
        failed_in_batch = 0

        for i, item in enumerate(batch):
            repo_base, pr_num = parse_pr_id(item['id'])
            if not repo_base:
                print(f"  [{i+1}/{len(batch)}] SKIP {item['id']} - parse error")
                batch_progress.append({
                    'item_id': item['id'],
                    'status': 'FAILED',
                    'reason': 'Parse error',
                    'timestamp': datetime.utcnow().isoformat()
                })
                failed_in_batch += 1
                continue

            repo = map_repo_to_github(repo_base)

            # Build close comment with evidence
            evidence = item.get('evidence', 'See master list')
            if 'markdown/progress' in evidence:
                comment = f"""This PR is being closed as it contains only documentation and progress updates, with no real code changes.

**Evidence:** {evidence}
**Reference:** task-20260817-134841-close-the-master-pendency-list-items-syn
**Classification:** DOCS_ONLY_NO_CODE"""
            else:
                comment = f"""This PR is being closed per the master pendency list analysis.

**Evidence:** {evidence}
**Reference:** task-20260817-134841-close-the-master-pendency-list-items-syn"""

            # Execute close synchronously
            success, stdout, stderr = close_pr_via_gh(repo, pr_num, comment)

            if success:
                print(f"  [{i+1}/{len(batch)}] CLOSED {item['id']}")
                batch_progress.append({
                    'item_id': item['id'],
                    'status': 'CLOSED',
                    'repo': repo,
                    'pr_num': pr_num,
                    'timestamp': datetime.utcnow().isoformat()
                })
                closed_in_batch += 1
            else:
                error_msg = stderr[:200] if stderr else "Unknown error"
                print(f"  [{i+1}/{len(batch)}] FAILED {item['id']}: {error_msg[:50]}...")
                batch_progress.append({
                    'item_id': item['id'],
                    'status': 'FAILED',
                    'repo': repo,
                    'pr_num': pr_num,
                    'error': error_msg,
                    'timestamp': datetime.utcnow().isoformat()
                })
                failed_in_batch += 1

        # Write progress after each batch
        write_progress_log(batch_progress)
        print(f"  Batch {batch_num + 1} complete: {closed_in_batch} closed, {failed_in_batch} failed")
        print()

        # STEP 3: Verify batch actually closed
        print(f"  Verifying batch {batch_num + 1}...")
        verified_closed = 0
        verification_updates = []

        for item in batch:
            repo_base, pr_num = parse_pr_id(item['id'])
            if not repo_base:
                continue

            repo = map_repo_to_github(repo_base)
            state = get_pr_state(repo, pr_num)

            if state == 'CLOSED':
                verified_closed += 1
            else:
                # If not closed, update log
                print(f"    WARNING: {item['id']} state={state} (expected CLOSED)")
                verification_updates.append({
                    'item_id': item['id'],
                    'status': 'FAILED',
                    'reason': f'Post-close verification: state={state}',
                    'timestamp': datetime.utcnow().isoformat()
                })

        if verification_updates:
            write_progress_log(verification_updates)

        print(f"  Verification: {verified_closed}/{len(batch)} confirmed closed")
        print()

    # STEP 4: Final summary
    print("="*70)
    print("STEP 4: Final Summary")
    print("="*70)

    final_progress = read_progress_log()
    final_counts = {
        'CLOSED': len([e for e in final_progress if e['status'] == 'CLOSED']),
        'FAILED': len([e for e in final_progress if e['status'] == 'FAILED']),
        'SKIPPED': len([e for e in final_progress if e['status'] == 'SKIPPED']),
    }

    print(f"Total items processed this run:")
    print(f"  Closed:  {final_counts['CLOSED']}")
    print(f"  Failed:  {final_counts['FAILED']}")
    print(f"  Skipped: {final_counts['SKIPPED']}")
    print(f"  Total:   {final_counts['CLOSED'] + final_counts['FAILED'] + final_counts['SKIPPED']}")

    if final_counts['FAILED'] > 0:
        print(f"\nFailed items:")
        for entry in final_progress:
            if entry['status'] == 'FAILED':
                print(f"  - {entry['item_id']}: {entry.get('reason', entry.get('error', 'Unknown'))}")

    print(f"\nExecution log written to: close_progress_log.jsonl")

if __name__ == '__main__':
    main()
