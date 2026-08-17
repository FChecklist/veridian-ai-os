#!/usr/bin/env python3
"""
Corrected conservative deduplication pass.

task-20260817-130826's identify_duplicates_conservative.py (reused
unmodified by AUDIT_VERIFICATION.md, which called it "conservative...
no false positive groupings detected") has a real bug, confirmed by
inspection here: `has_explicit_reference()` treats (a) ANY co-mention
of one PR's number inside another's title, or (b) ANY shared generic
keyword ('duplicate', 'supersed', 'replac', 'revert', 'undo') anywhere
in both titles -- as "explicit cross-reference" evidence, with no
requirement that the keyword and the number are actually about each
other. Because this repo's RCA/status-check PR titles routinely say
things like "closed as duplicate of PR #NNNN" or "already reverted",
that turned into a single-linkage chain that swept 44 completely
unrelated PRs (RCA of different incidents, cost governance, model
lifecycle, docs lifecycle, etc.) into one fake "duplicate group"
anchored on compliance-tracker#1289, plus a few smaller false pairs
(e.g. veridian-scripts#407-followup <-> #163-followup, matched only
because both titles happen to contain the substring "duplicate").

This script keeps the same conservative philosophy and the same two
evidence types (title similarity, explicit reference) but requires the
explicit-reference evidence to be genuinely explicit: a duplicate/
supersede/replace/revert/undo keyword must appear within 30 characters
of the SPECIFIC PR number being referenced, not just anywhere in the
title. Plain co-mention of a PR number with no such keyword nearby is
no longer treated as evidence.
"""
import json
import re
from difflib import SequenceMatcher

SOURCE_RAW = '/opt/veridian/ai-os/tasks/task-20260817-130826-enumerate-and-deduplicate-all-pendency-s/workspace/raw_enumeration.json'
OUT_PATH = '/opt/veridian/ai-os/tasks/task-20260817-141839-fix-fabricated-pendency-list-self-audit/workspace/duplicate_groups_reconfirmed.json'

KEYWORD_NUM_RE = re.compile(
    r'(?:duplicate(?:s|d)?(?:\s+of)?|supersed(?:e|es|ed|ing)?|replac(?:e|es|ed|ing)?|'
    r'revert(?:s|ed|ing)?(?:\s+of)?|undo(?:es|ne)?)\D{0,30}?#?(\d+)',
    re.IGNORECASE
)


def similarity_ratio(s1, s2):
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()


def keyword_anchored_refs(title):
    """PR numbers that a duplicate/supersede/replace/revert/undo keyword
    in this title is actually talking about (number within 30 chars of
    the keyword), not just any number mentioned anywhere."""
    return set(KEYWORD_NUM_RE.findall(title))


def own_num(item_id):
    m = re.search(r'#(\d+)', item_id)
    return m.group(1) if m else None


def has_explicit_reference(row1, row2):
    refs1 = keyword_anchored_refs(row1['title'])
    refs2 = keyword_anchored_refs(row2['title'])
    n1, n2 = own_num(row1['item_id']), own_num(row2['item_id'])
    if n2 and n2 in refs1:
        return True
    if n1 and n1 in refs2:
        return True
    return False


def main():
    with open(SOURCE_RAW) as f:
        rows = json.load(f)

    duplicate_groups = []
    seen = set()
    for i, row1 in enumerate(rows):
        if i in seen:
            continue
        group = [i]
        seen.add(i)
        for j, row2 in enumerate(rows[i + 1:], start=i + 1):
            if j in seen:
                continue
            if row1['item_type'] != row2['item_type']:
                continue
            if row1['repo'] != row2['repo']:
                continue
            title_sim = similarity_ratio(row1['title'], row2['title'])
            explicit = has_explicit_reference(row1, row2)
            if title_sim > 0.90 or explicit:
                group.append(j)
                seen.add(j)
        if len(group) > 1:
            duplicate_groups.append(group)

    details = []
    for group in duplicate_groups:
        group_rows = [rows[i] for i in group]
        details.append({
            'group_members': group,
            'member_ids': [rows[i]['item_id'] for i in group],
            'shared_repo': group_rows[0].get('repo'),
            'shared_type': group_rows[0].get('item_type'),
            'evidence': 'title_similarity_gt_0.90_or_keyword_anchored_explicit_reference',
        })

    out = {
        'total_rows': len(rows),
        'duplicate_groups': len(details),
        'method_note': (
            'Corrected version of task-20260817-130826 Step 3 conservative dedup. '
            'Same thresholds/philosophy, but explicit-reference evidence now requires '
            'a duplicate/supersede/replace/revert/undo keyword within 30 chars of the '
            'specific PR number, not mere co-mention or shared keyword anywhere in title. '
            'See dedupe_reconfirmed.py for the exact bug this fixes and why.'
        ),
        'details': details,
    }
    with open(OUT_PATH, 'w') as f:
        json.dump(out, f, indent=2)

    total_marked = sum(len(g['member_ids']) - 1 for g in details)
    print(f"groups={len(details)} total_duplicate_marked={total_marked}")
    for g in details:
        print(f"  size={len(g['member_ids'])}: {g['member_ids']}")


if __name__ == '__main__':
    main()
