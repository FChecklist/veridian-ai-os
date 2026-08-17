#!/bin/bash

# Enumerate merged PRs in date window (2026-07-15 to 2026-08-17) across target repos
REPOS=(
  "FChecklist/veridian-ai-os"
  "FChecklist/veridian-scripts"
  "FChecklist/projexa"
  "FChecklist/claude-control"
  "FChecklist/compliance-tracker"
)

WS="/opt/veridian/ai-os/tasks/task-20260817-130826-enumerate-and-deduplicate-all-pendency-s/workspace"

> "$WS/raw_merged_prs.jsonl"

# Query merged PRs merged in the window (use mergedAt as criterion)
# Note: GitHub API timezone is UTC, match the date window: 2026-07-15 to 2026-08-17
for repo in "${REPOS[@]}"; do
  echo "=== Merged PRs in $repo (2026-07-15 to 2026-08-17) ===" >&2

  # Query: merged PRs between two dates (using merged filter)
  gh pr list --repo "$repo" --state merged \
    --json number,title,createdAt,mergedAt,author,body,headRefName \
    --limit 2000 \
    | jq -r '.[] | select(.mergedAt >= "2026-07-15T00:00:00Z" and .mergedAt <= "2026-08-17T23:59:59Z") | {repo: "'$repo'", type: "pr", status: "merged"} + .' >> "$WS/raw_merged_prs.jsonl" 2>/dev/null || true
done

echo "Total lines for merged: $(grep -c 'number' "$WS/raw_merged_prs.jsonl" 2>/dev/null || echo 0)" >&2
