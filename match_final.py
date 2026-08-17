#!/usr/bin/env python3
import json
import re

target = json.load(open("target_items_corrected.json"))
strong_index = json.load(open("strong_index_final.json"))
weak_index = json.load(open("weak_index_final.json"))
snippet_index = json.load(open("snippet_index_final.json"))

# Exclude this exact task chain's own meta/process tasks (about the
# pendency list itself, not real dispatched merge/revise/implement work on
# an individual item) from counting as coverage, per SPEC objective.
EXCLUDE_DIRNAME_PREFIXES = (
    "task-20260817-130826-enumerate-and-deduplicate-all-pendency-s",
    "task-20260817-130836-close-every-item-on-the-master-pendency",
    "task-20260817-130843-certify-or-refuse-the-pendency-closure-a",
    "task-20260817-132903-close-every-item-on-the-master-pendency",
    "task-20260817-132910-certify-or-refuse-the-pendency-closure-a",
    "task-20260817-134841-close-the-master-pendency-list-items-syn",
    "task-20260817-134849-certify-or-refuse-the-pendency-closure-a",
    "task-20260817-140447-certify-or-refuse-the-pendency-closure-a",
    "task-20260817-141839-fix-fabricated-pendency-list-self-audit",
    "task-20260817-141859-map-real-task-queue-coverage-for-the-411",
)

def is_excluded(dirname):
    return dirname.startswith(EXCLUDE_DIRNAME_PREFIXES)

def repo_short(full_repo):
    return full_repo.split('/')[-1]

def parse_item(it):
    m = re.match(r'^([a-zA-Z0-9_.\-]+)#(\d+)(.*)$', it["id"])
    repo, num, suffix = m.groups()
    return repo, int(num), suffix

results = []
for it in target:
    repo, num, suffix = parse_item(it)
    repo_full = it.get("repo", "")
    repo_s = repo_short(repo_full) if repo_full else repo
    is_followup = suffix.startswith("-followup")
    key = f"{repo_s}#{num}"

    direct = [d for d in strong_index.get(key, []) if not is_excluded(d["dirname"])]
    plausible = [p for p in weak_index.get(key, []) if not is_excluded(p["dirname"])]

    for d in direct:
        d["snippet"] = snippet_index.get(f"{d['dirname']}::{key}", "")
    for p in plausible:
        p["snippet"] = snippet_index.get(f"{p['dirname']}::{key}", "")

    results.append({
        "item": it,
        "repo_short": repo_s,
        "pr_num": num,
        "is_followup": is_followup,
        "direct": direct,
        "plausible": plausible,
    })

n_direct = sum(1 for r in results if r["direct"])
n_plausible_only = sum(1 for r in results if not r["direct"] and r["plausible"])
n_none = sum(1 for r in results if not r["direct"] and not r["plausible"])
print(f"direct: {n_direct}  plausible-only: {n_plausible_only}  none: {n_none}  total: {len(results)}")

from collections import Counter
by_action = Counter()
direct_by_action = Counter()
plaus_by_action = Counter()
for x in results:
    action = x["item"]["recommended_action"]
    by_action[action] += 1
    if x["direct"]:
        direct_by_action[action] += 1
    elif x["plausible"]:
        plaus_by_action[action] += 1
print("by_action:", by_action)
print("direct_by_action:", direct_by_action)
print("plausible_by_action:", plaus_by_action)

with open("match_results_corrected.json", "w") as f:
    json.dump(results, f, indent=2)
