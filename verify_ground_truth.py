#!/usr/bin/env python3
"""
Step 2: Ground Truth Verification
For each row, check:
1. PR files changed (markdown-only vs real code)
2. Audit verdict in comments
3. Active worker units
"""

import json
import subprocess
import sys
import re
from collections import defaultdict

def get_pr_files(repo, pr_number):
    """Get list of files changed in a PR using gh CLI."""
    try:
        result = subprocess.run(
            ['gh', 'pr', 'view', str(pr_number), '--repo', repo, '--json', 'files'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get('files', [])
    except:
        pass
    return None

def has_real_code_changes(files):
    """Check if files list contains non-markdown, real source changes."""
    if not files:
        return None  # Unknown

    # Markdown/progress files that don't count as real changes
    exclude_patterns = [
        r'\.md$',
        r'progress/',
        r'PROGRESS\.md',
        r'\.txt$',
        r'\.yaml$',  # Config files often progress-tracking related
        r'notes/',
    ]

    real_files = []
    for f in files:
        path = f.get('path', '')
        is_excluded = any(re.search(p, path) for p in exclude_patterns)
        if not is_excluded:
            real_files.append(path)

    # If there are non-markdown files, there are real changes
    return len(real_files) > 0

def get_pr_comments(repo, pr_number):
    """Get comments on a PR, looking for audit verdicts."""
    try:
        result = subprocess.run(
            ['gh', 'pr', 'view', str(pr_number), '--repo', repo, '--json', 'comments'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get('comments', [])
    except:
        pass
    return None

def find_audit_verdict(comments):
    """Search comments for AUDIT: PASS or AUDIT: FAIL."""
    if not comments:
        return None

    for comment in comments:
        body = comment.get('body', '')
        if 'AUDIT: PASS' in body:
            return 'PASS'
        elif 'AUDIT: FAIL' in body:
            return 'FAIL'
    return None

def check_worker_units(task_name):
    """Check systemd for active worker units related to this task."""
    try:
        # Query user systemd for worker units
        result = subprocess.run(
            ['systemctl', '--user', 'list-units', '--all', '--no-pager'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            # Look for task name in units
            if task_name in result.stdout:
                return True
    except:
        pass
    return None  # Unknown/not verifiable

def main():
    # Read enumeration
    with open('raw_enumeration.json', 'r') as f:
        rows = json.load(f)

    print(f"Step 2: Verifying {len(rows)} rows for ground truth...")

    # Collect verification data
    verified_rows = []
    verification_stats = defaultdict(int)

    for i, row in enumerate(rows):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(rows)}", file=sys.stderr)

        item_id = row['item_id']
        item_type = row['item_type']
        repo = row['repo']

        # Extract PR number from item_id
        match = re.search(r'#(\d+)', item_id)
        pr_num = int(match.group(1)) if match else None

        # Verify based on type
        if item_type == 'pr' and pr_num:
            # Get files changed
            files = get_pr_files(repo, pr_num)
            row['_files_count'] = len(files) if files else None

            # Check for real code
            has_real = has_real_code_changes(files) if files else None
            row['has_real_code'] = has_real

            # Check for audit verdict
            comments = get_pr_comments(repo, pr_num)
            audit = find_audit_verdict(comments) if comments is not None else None
            row['audit_verdict'] = audit

            # Classify ground truth
            if has_real is None:
                row['ground_truth_status'] = 'UNVERIFIABLE'
                verification_stats['unverifiable'] += 1
            elif not has_real:
                row['ground_truth_status'] = 'MARKDOWN_ONLY'
                verification_stats['markdown_only'] += 1
            elif audit == 'FAIL':
                row['ground_truth_status'] = 'AUDIT_FAILED'
                verification_stats['audit_failed'] += 1
            else:
                row['ground_truth_status'] = 'REAL_CODE'
                verification_stats['real_code'] += 1
        else:
            # Followup items - just mark as seen
            row['ground_truth_status'] = 'FOLLOWUP_ITEM'
            verification_stats['followup'] += 1

        verified_rows.append(row)

    # Save verification results
    with open('verified_enumeration.json', 'w') as f:
        json.dump(verified_rows, f, indent=2)

    print("\nGround Truth Verification Complete:")
    print(f"  Real code PRs: {verification_stats['real_code']}")
    print(f"  Markdown-only: {verification_stats['markdown_only']}")
    print(f"  Audit failed: {verification_stats['audit_failed']}")
    print(f"  Unverifiable: {verification_stats['unverifiable']}")
    print(f"  Followup items: {verification_stats['followup']}")

    print(f"\nSaved verified data to verified_enumeration.json")

if __name__ == '__main__':
    main()
