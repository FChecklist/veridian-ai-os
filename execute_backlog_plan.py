#!/usr/bin/env python3
"""
execute_backlog_plan.py (ai-os operational entry point) -- THIN DELEGATOR.

SUPERSEDED 2026-07-27 following a real mass-mislabeling incident: this file
used to contain its own orchestration logic living outside any git
repository, driven by an equally-untracked, pre-fix copy of
plan_backlog_completion.py -- together they read a FROZEN, STALE
BACKLOG_COMPLETION_PLAN_2026-07-27.json and wrote its recorded category
verbatim into real task.yaml files at execution time, with no
SUCCESS_CRITERIA re-verification. That is what actually produced the 32
real task.yaml files hand-mislabeled status=superseded/completed this
morning. See PR #102 (claude-control) for the real root-cause fix.

This file is no longer allowed to contain its own copy of that orchestration
logic. It delegates entirely, by process replacement (os.execv), to the
fixed, tested, git-tracked scripts/execute_backlog_plan.py in the
claude-control repo checkout -- same argv, same behavior, and (via that
file) the fixed, SUCCESS_CRITERIA-verifying plan_backlog_completion.py for
every classify/verify/write decision. There is now exactly one real
implementation of this pipeline; this file is just how the ai-os
operational surface reaches it.
"""
import os
import sys

CLAUDE_CONTROL_REPO = os.environ.get("CLAUDE_CONTROL_REPO", "/opt/veridian/repos/claude-control")
FIXED_SCRIPT = os.path.join(CLAUDE_CONTROL_REPO, "scripts", "execute_backlog_plan.py")


def main():
    if not os.path.isfile(FIXED_SCRIPT):
        sys.exit(
            f"FATAL: fixed orchestration script not found at {FIXED_SCRIPT} -- this delegator refuses "
            f"to fall back to any local/independent orchestration logic (that is exactly how the "
            f"2026-07-27 incident happened). Set CLAUDE_CONTROL_REPO if the claude-control repo "
            f"checkout lives elsewhere on this host."
        )
    os.execv(sys.executable, [sys.executable, FIXED_SCRIPT] + sys.argv[1:])


if __name__ == "__main__":
    main()
