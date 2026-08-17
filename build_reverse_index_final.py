#!/usr/bin/env python3
"""
Final reverse-index build, using the corrected task_index2.json (real,
per-task-attributed prompt + progress text; no cross-task progress-dir
contamination, no truncated-dirname PR-number guessing).

Two independent signal types, both grounded in real per-task text:
 - STRONG: an explicit "github.com/<owner>/<repo>/pull/<num>" URL (fully
   unambiguous), OR repo short-name + PR-number token within TIGHT_WINDOW
   chars of each other.
 - WEAK/plausible: repo short-name + PR-number token within WIDE_WINDOW
   chars but not TIGHT_WINDOW.
"""
import json
import re
from collections import defaultdict

idx = json.load(open("task_index2.json"))
qm = json.load(open("queue_status_map.json"))
verifiable = [e for e in idx if e["id"][:46] in qm]
print(f"{len(verifiable)} verifiable task dirs")

REPOS = ["claude-control", "compliance-tracker", "veridian-scripts", "projexa", "veridian-ai-os"]
repo_re = re.compile('|'.join(re.escape(r) for r in REPOS))
pr_token_re = re.compile(r'(?:(?<![\w-])pr[\-_ #]*(\d+)(?!\d))|(?:(?<!\d)#(\d+)(?!\d))', re.I)
url_re = re.compile(
    r'github\.com/[\w.-]+/(' + '|'.join(re.escape(r) for r in REPOS) + r')/pull/(\d+)', re.I
)

TIGHT_WINDOW = 30
WIDE_WINDOW = 150

strong_index = defaultdict(list)
weak_index = defaultdict(list)
snippet_index = {}

for e in verifiable:
    blob = "\n".join([e.get("title", ""), e["_blob"]])
    tinfo = {"id": e["id"], "dirname": e["dirname"], "status_live": qm[e["id"][:46]]["status"]}

    seen_strong = set()
    seen_weak = set()

    # 1) explicit PR URL -- unambiguous, always strong
    for m in url_re.finditer(blob):
        repo = m.group(1)
        num = int(m.group(2))
        key = f"{repo}#{num}"
        if key not in seen_strong:
            seen_strong.add(key)
            strong_index[key].append(tinfo)
            snippet_index[f"{e['dirname']}::{key}"] = blob[max(0, m.start() - 90):m.end() + 60]

    # 2) proximity of repo-name token + PR-number token
    repo_hits = [(m.start(), m.group(0)) for m in repo_re.finditer(blob)]
    pr_hits = [(m.start(), m.end(), int(m.group(1) or m.group(2))) for m in pr_token_re.finditer(blob)]

    for pr_start, pr_end, num in pr_hits:
        best_tight = None
        best_wide = None
        for repo_pos, repo_name in repo_hits:
            dist = min(abs(repo_pos - pr_start), abs(repo_pos - pr_end))
            if dist <= TIGHT_WINDOW:
                best_tight = repo_name
                break
            if dist <= WIDE_WINDOW and best_wide is None:
                best_wide = repo_name
        target_repo = best_tight or best_wide
        if not target_repo:
            continue
        key = f"{target_repo}#{num}"
        if best_tight and key not in seen_strong:
            seen_strong.add(key)
            strong_index[key].append(tinfo)
            snippet_index.setdefault(f"{e['dirname']}::{key}", blob[max(0, pr_start - 90):pr_end + 90])
        elif best_wide and key not in seen_weak and key not in seen_strong:
            seen_weak.add(key)
            weak_index[key].append(tinfo)
            snippet_index.setdefault(f"{e['dirname']}::{key}", blob[max(0, pr_start - 90):pr_end + 90])

print("strong_index keys:", len(strong_index))
print("weak_index keys:", len(weak_index))
json.dump(strong_index, open("strong_index_final.json", "w"))
json.dump(weak_index, open("weak_index_final.json", "w"))
json.dump(snippet_index, open("snippet_index_final.json", "w"))
print("done")
