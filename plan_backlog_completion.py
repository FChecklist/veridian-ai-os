#!/usr/bin/env python3
"""
plan_backlog_completion.py (ai-os operational entry point) -- THIN DELEGATOR.

SUPERSEDED 2026-07-27 following a real mass-mislabeling incident: this file
used to contain its own, independent, unverified copy of the dedup/classify
logic living outside any git repository -- no SUCCESS_CRITERIA
re-verification before concluding ALREADY_DONE_STALE_STATUS, no --apply
write guard, no --audit-report mode. That untracked copy (paired with
/opt/veridian/ai-os/execute_backlog_plan.py) is what actually produced the
32 real task.yaml files hand-mislabeled status=superseded/completed this
morning, purely because a PR number mentioned somewhere in an rca-chain's
checkpoint prose happened to be merged -- with no check that the merged
PR's real diff satisfied the original task's own SUCCESS_CRITERIA. See PR
#102 (claude-control) for the real root-cause fix.

This file is no longer allowed to contain its own copy of that logic. It
delegates entirely, by process replacement (os.execv), to the fixed,
tested, git-tracked scripts/plan_backlog_completion.py in the claude-control
repo checkout -- same argv, same behavior, real SUCCESS_CRITERIA
verification and the --apply / --audit-report guarded write paths. There is
now exactly one real implementation of this dedup routine; this file is
just how the ai-os operational surface reaches it.
"""
import os
import sys

CLAUDE_CONTROL_REPO = os.environ.get("CLAUDE_CONTROL_REPO", "/opt/veridian/repos/claude-control")
FIXED_SCRIPT = os.path.join(CLAUDE_CONTROL_REPO, "scripts", "plan_backlog_completion.py")


def main():
    if not os.path.isfile(FIXED_SCRIPT):
        sys.exit(
            f"FATAL: fixed dedup classifier not found at {FIXED_SCRIPT} -- this delegator refuses to "
            f"fall back to any local/independent dedup logic (that is exactly how the 2026-07-27 "
            f"incident happened). Set CLAUDE_CONTROL_REPO if the claude-control repo checkout lives "
            f"elsewhere on this host."
        )
    os.execv(sys.executable, [sys.executable, FIXED_SCRIPT] + sys.argv[1:])


if __name__ == "__main__":
    main()
