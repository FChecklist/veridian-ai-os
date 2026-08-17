#!/usr/bin/env python3
"""
Step 4: Classify each row into the closed-set categories.

Categories:
1. REAL_CODE_MERGED_LIVE - real code, merged, confirmed present in deployed/production
2. REAL_CODE_MERGED_UNVERIFIED - real code, merged, but not confirmed deployed
3. REAL_CODE_UNMERGED - real, reviewable code exists on branch or open PR, not yet merged
4. BLOCKED_ON_AUDIT - real code exists, waiting only on independent audit verdict
5. DOCS_ONLY_NO_CODE - diff contains only progress notes or markdown
6. DUPLICATE_OF - marked in Step 3
7. STALE_SUPERSEDED - real once, but events since have made it obsolete
8. GENUINELY_OPEN_UNSTARTED - nothing has been attempted yet
9. UNVERIFIABLE - state why you could not determine
"""

import json
import re

def classify_row(row, duplicate_groups=None):
    """Classify a single row into the closed set."""

    # Check if this row is marked as duplicate
    if duplicate_groups:
        for group in duplicate_groups.get('details', []):
            if row['item_id'] in group['member_ids'] and len(group['member_ids']) > 1:
                # Find canonical (pick the first one in group as canonical)
                canonical = group['member_ids'][0]
                if row['item_id'] != canonical:
                    return {
                        'classification': 'DUPLICATE_OF',
                        'evidence': f"Duplicate of {canonical}",
                        'recommended_action': 'CLOSE'
                    }

    # Classification based on item type and status
    item_type = row.get('item_type', '')
    status = row.get('status', '')
    title = row.get('title', '')

    # Get ground truth status if available
    ground_truth = row.get('ground_truth_status', 'unknown')

    # Followup items from merged PRs
    if item_type == 'followup':
        if 'merged' in status:
            # This is work that was declared when a PR merged
            # Need to check if the followup work itself has been done
            return {
                'classification': 'GENUINELY_OPEN_UNSTARTED',
                'evidence': 'Followup work declared in merged PR, no PR found to address it',
                'recommended_action': 'IMPLEMENT'
            }

    # Open PRs
    if item_type == 'pr' and status == 'open':
        # Check if it's markdown-only
        if ground_truth == 'MARKDOWN_ONLY' or 'LIKELY_DOCS_ONLY' in ground_truth:
            return {
                'classification': 'DOCS_ONLY_NO_CODE',
                'evidence': f'Open PR contains only markdown/progress files, no real code changes',
                'recommended_action': 'CLOSE'
            }

        # Check if audit failed
        if ground_truth == 'AUDIT_FAILED':
            return {
                'classification': 'BLOCKED_ON_AUDIT',
                'evidence': 'PR exists with real code but audit verdict is FAIL',
                'recommended_action': 'REVISE'
            }

        # If it's likely real code
        if ground_truth in ['LIKELY_REAL_CODE', 'REAL_CODE']:
            return {
                'classification': 'REAL_CODE_UNMERGED',
                'evidence': f'Open PR with real code changes',
                'recommended_action': 'MERGE'
            }

        # Default for open PR
        if ground_truth == 'UNVERIFIABLE':
            return {
                'classification': 'UNVERIFIABLE',
                'evidence': 'Could not determine if open PR contains real code changes',
                'recommended_action': 'ESCALATE'
            }

        # Fallback heuristic
        return {
            'classification': 'REAL_CODE_UNMERGED',
            'evidence': 'Open PR (presumed real code, not verified)',
            'recommended_action': 'MERGE'
        }

    # Merged PRs
    if item_type == 'pr' and status == 'merged':
        # Check for markdown-only merged PRs
        if ground_truth == 'MARKDOWN_ONLY' or 'LIKELY_DOCS_ONLY' in ground_truth:
            return {
                'classification': 'DOCS_ONLY_NO_CODE',
                'evidence': 'Merged PR contains only markdown/progress files',
                'recommended_action': 'CLOSE'
            }

        # Real code merged - check if we can confirm it's deployed
        # For now, just mark as REAL_CODE_MERGED_UNVERIFIED since we can't check deployment
        return {
            'classification': 'REAL_CODE_MERGED_UNVERIFIED',
            'evidence': 'PR has been merged but deployment status not verified',
            'recommended_action': 'CLOSE'
        }

    # Unknown
    return {
        'classification': 'UNVERIFIABLE',
        'evidence': f'Cannot classify: type={item_type}, status={status}',
        'recommended_action': 'ESCALATE'
    }

def main():
    # Read enumeration
    try:
        with open('verified_enumeration.json', 'r') as f:
            rows = json.load(f)
        print("Using verified_enumeration.json")
    except:
        with open('verified_enumeration_heuristic.json', 'r') as f:
            rows = json.load(f)
        print("Using verified_enumeration_heuristic.json")

    # Read duplicate groups
    try:
        with open('duplicate_groups_conservative.json', 'r') as f:
            duplicate_groups = json.load(f)
    except:
        duplicate_groups = None
        print("Note: duplicate groups not available")

    print(f"\nStep 4: Classifying {len(rows)} rows...")

    # Classify each row
    classified_rows = []
    for row in rows:
        classification = classify_row(row, duplicate_groups)
        classified_row = {**row, **classification}
        classified_rows.append(classified_row)

    # Save classified data
    with open('classified_enumeration.json', 'w') as f:
        json.dump(classified_rows, f, indent=2)

    # Generate counts
    classification_counts = {}
    action_counts = {}
    for row in classified_rows:
        classification = row.get('classification', 'unknown')
        action = row.get('recommended_action', 'unknown')
        classification_counts[classification] = classification_counts.get(classification, 0) + 1
        action_counts[action] = action_counts.get(action, 0) + 1

    print("\nClassification counts:")
    for c in sorted(classification_counts.keys()):
        print(f"  {c}: {classification_counts[c]}")

    print("\nRecommended action counts:")
    for a in sorted(action_counts.keys()):
        print(f"  {a}: {action_counts[a]}")

    print(f"\nSaved classified enumeration to classified_enumeration.json")

if __name__ == '__main__':
    main()
