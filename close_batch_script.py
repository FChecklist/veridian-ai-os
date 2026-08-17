#!/usr/bin/env python3
"""Script to close CLOSE-action items from the master list."""

import yaml
import json
import subprocess
import sys
from collections import defaultdict

def load_master_list():
    """Load the master list."""
    with open('master_list.yaml', 'r') as f:
        return yaml.safe_load(f)

def get_close_items(master_list):
    """Get all items with CLOSE action."""
    return [item for item in master_list['items'] if item['recommended_action'] == 'CLOSE']

def parse_pr_id(pr_id):
    """Parse PR ID like 'compliance-tracker#558' into (repo_base, repo_num)."""
    parts = pr_id.split('#')
    if len(parts) != 2:
        return None, None
    repo_base = parts[0]  # e.g., "compliance-tracker"
    pr_num = parts[1]     # e.g., "558"
    return repo_base, pr_num

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

def close_pr_via_gh(repo, pr_num, comment):
    """Close a PR using gh CLI."""
    cmd = [
        'gh', 'pr', 'close', pr_num,
        '--repo', repo,
        '--comment', comment
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, '', str(e)

def main():
    master_list = load_master_list()
    close_items = get_close_items(master_list)

    print(f"Total CLOSE items to process: {len(close_items)}")
    print()

    # Group by evidence
    evidence_groups = defaultdict(list)
    for item in close_items:
        evidence = item.get('evidence', 'unknown')
        evidence_groups[evidence].append(item)

    # Print summary
    for evidence, items in sorted(evidence_groups.items(), key=lambda x: -len(x[1]))[:5]:
        print(f"[{len(items)}] {evidence}")

    print("\nGenerating close report (dry-run, no actual closes yet)...")

    # Generate report
    closed_count = 0
    failed_count = 0

    for i, item in enumerate(close_items[:10]):  # Start with first 10 for testing
        repo_base, pr_num = parse_pr_id(item['id'])
        if not repo_base:
            print(f"[SKIP] {item['id']} - could not parse")
            failed_count += 1
            continue

        repo = map_repo_to_github(repo_base)

        # Prepare comment
        if "markdown/progress" in item.get('evidence', ''):
            close_comment = f"""This PR is being closed as it contains only documentation and progress updates, with no real code changes.

**Evidence:** {item['evidence']}

**Master List Reference:** task-20260817-132903-close-every-item-on-the-master-pendency
**Classification:** DOCS_ONLY_NO_CODE
"""
        else:
            close_comment = f"""This PR is being closed per the master pendency list.

**Evidence:** {item['evidence']}

**Master List Reference:** task-20260817-132903-close-every-item-on-the-master-pendency
"""

        print(f"\n[{i+1}] {item['id']} -> {repo}#{pr_num}")
        print(f"    Would close with: {close_comment[:80]}...")

    print(f"\nDry-run complete: examined {min(10, len(close_items))} items")
    print("Ready to execute actual closes on confirmation.")

if __name__ == '__main__':
    main()
