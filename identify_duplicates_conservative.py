#!/usr/bin/env python3
"""
Step 3: Identify Duplicates (CONSERVATIVE approach)
Only mark as duplicates when there is STRONG evidence:
- Very high title similarity (>0.90)
- Explicit cross-references (one PR references the other)
- Same target item and type

Avoids false positives from "same repo + somewhat similar title"
"""

import json
import re
from difflib import SequenceMatcher

def similarity_ratio(s1, s2):
    """Calculate string similarity ratio."""
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

def extract_pr_numbers(text):
    """Extract all PR numbers referenced in text."""
    return set(re.findall(r'#(\d+)', text))

def has_explicit_reference(row1, row2):
    """Check if one row explicitly references the other."""
    # Extract PR numbers from both
    nums1 = extract_pr_numbers(row1['title'])
    nums2 = extract_pr_numbers(row2['title'])

    # Get their own numbers
    own_num1 = extract_pr_numbers(row1['item_id'])
    own_num2 = extract_pr_numbers(row2['item_id'])

    # Check cross-references
    if own_num2 & nums1 or own_num1 & nums2:
        return True

    # Check for supersedes/replacement keywords
    keywords = ['supersed', 'replac', 'duplicate', 'revert', 'undo']
    for kw in keywords:
        if kw in row1['title'].lower() and kw in row2['title'].lower():
            return True

    return False

def main():
    # Read enumeration
    try:
        with open('verified_enumeration.json', 'r') as f:
            rows = json.load(f)
        print("Using verified_enumeration.json")
    except:
        with open('raw_enumeration.json', 'r') as f:
            rows = json.load(f)
        print("Using raw_enumeration.json (verification not complete)")

    print(f"\nStep 3 (CONSERVATIVE): Identifying duplicates among {len(rows)} rows...")

    # Group candidates by STRONG evidence only
    duplicate_groups = []
    seen_indices = set()

    for i, row1 in enumerate(rows):
        if i in seen_indices:
            continue

        group = [i]
        seen_indices.add(i)

        # Look for definite duplicates
        for j, row2 in enumerate(rows[i+1:], start=i+1):
            if j in seen_indices:
                continue

            # Must be same type
            if row1['item_type'] != row2['item_type']:
                continue

            # Check for strong evidence
            title_sim = similarity_ratio(row1['title'], row2['title'])
            has_explicit = has_explicit_reference(row1, row2)

            # Only mark as duplicate if:
            # 1. Very high similarity (>0.90)
            # 2. OR explicit cross-reference
            # 3. AND same repository (to avoid cross-repo false positives)
            if row1['repo'] == row2['repo'] and (title_sim > 0.90 or has_explicit):
                group.append(j)
                seen_indices.add(j)
                print(f"  Duplicate: {row1['item_id']} <-> {row2['item_id']} (sim={title_sim:.2f}, explicit={has_explicit})")

        if len(group) > 1:
            duplicate_groups.append(group)

    print(f"\nFound {len(duplicate_groups)} duplicate groups with strong evidence")

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
            'evidence': 'high_similarity_or_explicit_reference'
        }
        duplicate_info['details'].append(group_info)

    with open('duplicate_groups_conservative.json', 'w') as f:
        json.dump(duplicate_info, f, indent=2)

    print(f"Saved conservative duplicate analysis to duplicate_groups_conservative.json")

if __name__ == '__main__':
    main()
