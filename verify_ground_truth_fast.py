#!/usr/bin/env python3
"""
Fast heuristic verification when full gh CLI verification is too slow.
Uses local branch/file information instead of remote queries.
"""

import json
import subprocess
import re
from pathlib import Path

def check_if_branch_exists(repo, branch_name):
    """Check if a branch exists in local clones or via git."""
    try:
        # Try to list branch in the repo
        result = subprocess.run(
            ['gh', 'api', f'repos/{repo}/branches', '--paginate'],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            branches = [b.get('name', '') for b in data if isinstance(data, list)]
            return branch_name in branches
    except:
        pass
    return None

def extract_branch_from_pr_data(pr_data):
    """Extract branch name from PR data if available."""
    return pr_data.get('headRefName', '')

def classify_by_heuristics(row):
    """Classify ground truth based on simple heuristics."""
    item_type = row.get('item_type', '')
    status = row.get('status', '')
    title = row.get('title', '')

    # Followup items are known to need work
    if item_type == 'followup':
        return 'FOLLOWUP_ITEM'

    # Merged items with undone work
    if 'merged_with_undone' in status:
        return 'MERGED_WITH_UNDONE_FOLLOWUP'

    # Open PRs are unmerged real code
    if item_type == 'pr' and status == 'open':
        # Check if title indicates it's just docs/progress
        if re.search(r'docs|progress|readme|memo|note', title, re.IGNORECASE):
            return 'LIKELY_DOCS_ONLY'
        return 'LIKELY_REAL_CODE'

    # Unknown
    return 'UNCLASSIFIABLE'

def main():
    # Read enumeration
    try:
        with open('verified_enumeration.json', 'r') as f:
            rows = json.load(f)
            print("Using already-completed verified_enumeration.json")
            return
    except:
        pass

    print("Running fast heuristic verification (real gh CLI verification may still be running)")

    with open('raw_enumeration.json', 'r') as f:
        rows = json.load(f)

    # Apply heuristic classification
    for row in rows:
        row['ground_truth_status'] = classify_by_heuristics(row)
        row['verification_method'] = 'heuristic'

    # Save results
    with open('verified_enumeration_heuristic.json', 'w') as f:
        json.dump(rows, f, indent=2)

    # Count results
    stats = {}
    for row in rows:
        status = row.get('ground_truth_status', 'unknown')
        stats[status] = stats.get(status, 0) + 1

    print("\nHeuristic Classification Results:")
    for status, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {status}: {count}")

if __name__ == '__main__':
    main()
