#!/usr/bin/env python3
"""
Step 3: Identify Duplicates
Find rows that address the same underlying objective:
- Overlapping changed-file sets
- Near-identical objective text
- One explicitly superseding another
"""

import json
import re
from difflib import SequenceMatcher

def similarity_ratio(s1, s2):
    """Calculate string similarity ratio."""
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

def extract_repo_name(repo_path):
    """Extract short repo name from full path."""
    return repo_path.split('/')[-1]

def main():
    # Read verified enumeration (or raw if verification not done yet)
    try:
        with open('verified_enumeration.json', 'r') as f:
            rows = json.load(f)
        print("Using verified_enumeration.json")
    except:
        with open('raw_enumeration.json', 'r') as f:
            rows = json.load(f)
        print("Using raw_enumeration.json (verification not complete)")

    print(f"\nStep 3: Identifying duplicates among {len(rows)} rows...")

    # Group candidates by similarity
    duplicate_groups = []
    seen_indices = set()

    for i, row1 in enumerate(rows):
        if i in seen_indices:
            continue

        group = [i]
        seen_indices.add(i)

        # Look for potential duplicates
        for j, row2 in enumerate(rows[i+1:], start=i+1):
            if j in seen_indices:
                continue

            # Skip if different repos and both are PRs (different repos = different items)
            # But allow cross-repo if they're both followups addressing same underlying work
            same_repo = row1['repo'] == row2['repo']

            # Check title similarity
            title_sim = similarity_ratio(row1['title'], row2['title'])

            # Check for explicit references
            explicit_ref = (
                f"#{row1['item_id'].split('#')[-1]}" in row2['title'] or
                f"#{row2['item_id'].split('#')[-1]}" in row1['title'] or
                'supersed' in row1['title'].lower() or
                'supersed' in row2['title'].lower() or
                'duplicate' in row1['title'].lower() or
                'duplicate' in row2['title'].lower()
            )

            # Same type and very similar title = likely duplicate
            if (row1['item_type'] == row2['item_type'] and
                (title_sim > 0.75 or explicit_ref)):
                if same_repo or row1['item_type'] == 'followup':
                    group.append(j)
                    seen_indices.add(j)
                    print(f"  Duplicate pair: {row1['item_id']} <-> {row2['item_id']} (sim={title_sim:.2f})")

        if len(group) > 1:
            duplicate_groups.append(group)

    print(f"\nFound {len(duplicate_groups)} duplicate groups")

    # Save duplicate information
    duplicate_info = {
        'total_rows': len(rows),
        'duplicate_groups': len(duplicate_groups),
        'details': []
    }

    for group in duplicate_groups:
        group_rows = [rows[i] for i in group]
        group_info = {
            'group_members': group,
            'member_ids': [rows[i]['item_id'] for i in group],
            'shared_repo': group_rows[0].get('repo') if group_rows else None,
            'shared_type': group_rows[0].get('item_type') if group_rows else None,
        }
        duplicate_info['details'].append(group_info)

    with open('duplicate_groups.json', 'w') as f:
        json.dump(duplicate_info, f, indent=2)

    print(f"Saved duplicate analysis to duplicate_groups.json")

if __name__ == '__main__':
    main()
