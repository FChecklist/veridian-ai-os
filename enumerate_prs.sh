#!/bin/bash

# Enumerate all open PRs across target repos
REPOS=(
  "FChecklist/veridian-ai-os"
  "FChecklist/veridian-scripts"
  "FChecklist/projexa"
  "FChecklist/claude-control"
  "FChecklist/compliance-tracker"
)

WS="/opt/veridian/ai-os/tasks/task-20260817-130826-enumerate-and-deduplicate-all-pendency-s/workspace"

> "$WS/raw_open_prs.jsonl"

for repo in "${REPOS[@]}"; do
  echo "=== Open PRs in $repo ===" >&2
  gh pr list --repo "$repo" --state open --json number,title,createdAt,updatedAt,author,headRefName --limit 1000 \
    | jq -r '.[] | {repo: "'$repo'", type: "pr", status: "open"} + .' >> "$WS/raw_open_prs.jsonl" 2>/dev/null || true
done

echo "Total lines: $(wc -l < "$WS/raw_open_prs.jsonl")" >&2
