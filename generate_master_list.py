#!/usr/bin/env python3
"""
Step 5: Generate the Master List

Produces a single YAML/JSON file containing every surviving row after dedup, with:
- id, type, repo, title, classification, evidence, recommended action
- Sorted by: recommended action, repo, age (oldest first)
- Final counts per classification and action
"""

import json
import yaml
from datetime import datetime
from pathlib import Path

def main():
    # Read classified enumeration
    try:
        with open('classified_enumeration.json', 'r') as f:
            rows = json.load(f)
    except FileNotFoundError:
        print("Error: classified_enumeration.json not found. Run classify_rows.py first.")
        return

    # Filter out duplicates (they should have recommended_action=CLOSE or be marked DUPLICATE_OF)
    # Actually, keep all rows but mark duplicates clearly

    # Prepare master list
    master_rows = []
    for row in rows:
        master_row = {
            'id': row.get('item_id', 'unknown'),
            'type': row.get('item_type', 'unknown'),
            'repo': row.get('repo', 'unknown'),
            'title': row.get('title', 'unknown'),
            'classification': row.get('classification', 'UNVERIFIABLE'),
            'evidence': row.get('evidence', 'No evidence provided'),
            'recommended_action': row.get('recommended_action', 'ESCALATE'),
            'status': row.get('status', 'unknown'),
            'created_date': row.get('created_date', ''),
            'link': row.get('link', ''),
        }
        master_rows.append(master_row)

    # Sort by: recommended_action, repo, created_date (oldest first)
    action_order = {
        'CLOSE': 0,
        'MERGE': 1,
        'AUDIT': 2,
        'IMPLEMENT': 3,
        'REVISE': 4,
        'RECOMMEND_DELETE': 5,
        'ESCALATE': 6,
    }

    def sort_key(row):
        action = row['recommended_action']
        action_priority = action_order.get(action, 99)
        repo = row['repo']
        date = row['created_date']
        return (action_priority, repo, date)

    sorted_rows = sorted(master_rows, key=sort_key)

    # Generate statistics
    classification_stats = {}
    action_stats = {}
    for row in master_rows:
        c = row['classification']
        a = row['recommended_action']
        classification_stats[c] = classification_stats.get(c, 0) + 1
        action_stats[a] = action_stats.get(a, 0) + 1

    # Build master list document
    master_list = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_items': len(master_rows),
            'duplicate_items': sum(1 for r in master_rows if r['classification'] == 'DUPLICATE_OF'),
            'surviving_items': len([r for r in master_rows if r['classification'] != 'DUPLICATE_OF']),
            'window_start': '2026-07-15',
            'window_end': '2026-08-17',
        },
        'statistics': {
            'by_classification': classification_stats,
            'by_recommended_action': action_stats,
        },
        'items': sorted_rows,
    }

    # Write as YAML
    with open('master_list.yaml', 'w') as f:
        yaml.dump(master_list, f, default_flow_style=False, sort_keys=False)

    # Also write as JSON for easier parsing
    with open('master_list.json', 'w') as f:
        json.dump(master_list, f, indent=2)

    print("Step 5: Master List Generated")
    print("=" * 60)
    print(f"\nTotal items processed: {master_list['metadata']['total_items']}")
    print(f"Duplicate items: {master_list['metadata']['duplicate_items']}")
    print(f"Surviving items: {master_list['metadata']['surviving_items']}")

    print("\nClassification Breakdown:")
    for classification in sorted(classification_stats.keys()):
        count = classification_stats[classification]
        print(f"  {classification}: {count}")

    print("\nRecommended Action Breakdown:")
    for action in sorted(action_stats.keys()):
        count = action_stats[action]
        print(f"  {action}: {count}")

    print("\nSorted by: Recommended Action -> Repo -> Age (oldest first)")
    print("\nMaster list saved to:")
    print("  - master_list.yaml (primary format)")
    print("  - master_list.json (alternative format)")

    # Print a sample of the first few items
    print("\nSample items (first 5):")
    for row in sorted_rows[:5]:
        print(f"\n  ID: {row['id']}")
        print(f"  Type: {row['type']}")
        print(f"  Repo: {row['repo']}")
        print(f"  Title: {row['title'][:60]}")
        print(f"  Classification: {row['classification']}")
        print(f"  Recommended Action: {row['recommended_action']}")

if __name__ == '__main__':
    main()
