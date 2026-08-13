# Boss/worker model-tier verification (task-20260813-035740)

Governing chain: addendum to P1 UMR-20260806-171945-5767, sibling of
UMR-20260813-034121-45c0. Checking the premise "BOSS=sonnet-high/
WORKER=haiku-low tiering already used by this dispatch pipeline" against
the real, live scripts before documenting anything.

## Canonical live pipeline location

This task's own repo checkout (`/opt/veridian/repos/claude-control/scripts/`)
is a stale copy (`resource_governor.py` dated Jul 27, 29942 bytes). The
live, actually-deployed copy is `/opt/veridian/scripts/` (`resource_governor.py`
dated Aug 8, 204462 bytes) -- confirmed via `diff` (stale copy is missing
~5x the content, including later hardening fixes). All evidence below is
from `/opt/veridian/scripts/`.

## What `resource_governor.py` tier 0-4 actually is

```
$ grep -n "^TIER_MIN\|^DEFAULT_TIER" /opt/veridian/scripts/resource_governor.py
68:TIER_MIN, TIER_MAX = 0, 4
69:DEFAULT_TIER = 2
```

Comment directly above (line 76-78): "Anti-starvation aging (design doc
'Dynamic realignment'): a queued item's effective priority is
max(0, tier - age_seconds // this interval)." `submit()`'s own docstring
(line ~841) confirms: this `tier` is a **scheduling/dispatch-queue priority**
(0=highest priority to run next .. 4=lowest), used for queue ordering and
anti-starvation aging in `umr_tasks`. It has no connection to which Claude
model gets invoked.

## The separate, unrelated "tier1/tier2" concept

`/opt/veridian/scripts/risk-tier.py` classifies a task's *diff* as
tier1 (Superboss may merge autonomously) or tier2 (must hold for human
sign-off), via `policy_decision.classify_risk_tier()`. This is a **risk/
governance** classification of a completed diff, also unrelated to model
selection. `supervisor-entrypoint.sh` uses this only to label the PR body
("Risk tier: $TIER").

## What model each real invocation actually uses

```
$ grep -n -- "--model" /opt/veridian/scripts/worker-entrypoint.sh
260:claude -p "$PROMPT" --model sonnet --effort high --dangerously-skip-permissions --max-budget-usd "$WORKER_BUDGET_CAP_USD" ...

$ grep -n -- "--model" /opt/veridian/scripts/supervisor-entrypoint.sh
117:  -p "$REVIEW_PROMPT" --model sonnet --effort high --dangerously-skip-permissions --max-budget-usd "$SUPERVISOR_B..." ...

$ grep -n -- "--model" /opt/veridian/scripts/doc-worker-entrypoint.sh
139:timeout "$MAX_WALL_SECONDS" claude -p "$PROMPT" --model sonnet --effort high --dangerously-skip-permissions ...

$ grep -n -- "--model" /opt/veridian/scripts/master-decompose.py
105:        ["claude", "-p", prompt, "--model", "sonnet", "--effort", "high", "--dangerously-skip-permissions", ...]

$ grep -n "CLAUDE_MODEL\|CLAUDE_EFFORT" /opt/veridian/scripts/gtm_check_ux_audit.py
137:CLAUDE_MODEL = "sonnet"
138:CLAUDE_EFFORT = "high"

$ grep -n "PM_TRIAGE_CLAUDE_MODEL" /opt/veridian/scripts/dispatch-tick.py
746:PM_TRIAGE_CLAUDE_MODEL = os.environ.get("VERIDIAN_PM_TRIAGE_CLAUDE_MODEL", "sonnet")
909:             "--model", PM_TRIAGE_CLAUDE_MODEL,
```

Every real Claude Code invocation found in `/opt/veridian/scripts/`
(worker-entrypoint.sh, doc-worker-entrypoint.sh, supervisor-entrypoint.sh,
master-decompose.py, gtm_check_ux_audit.py, dispatch-tick.py's PM triage)
uses **`sonnet` / `high`**, including the ones that run *worker* tasks, not
just the Superboss/supervisor review path.

```
$ grep -rln -i "haiku" /opt/veridian/scripts /opt/veridian/systemd /opt/veridian/repos/claude-control
/opt/veridian/scripts/credit-accountant.py        # docstring example: "write a haiku about..." -- unrelated
/opt/veridian/repos/claude-control/CONTROLLER.yaml            # an actual haiku-writing task row -- unrelated
/opt/veridian/repos/claude-control/VERIDIAN_Review_Framework_evaluated_2045rows.csv   # unrelated
/opt/veridian/repos/claude-control/ai-os/WIRING_ENGINE_REGISTRY_2026-07-25.json       # unrelated
```

No occurrence of `haiku` refers to a Claude model. `/opt/veridian/systemd/`
is empty (this task's workspace has its own unrelated `systemd/` dir with a
watchdog timer and webhook receiver unit, not worker/supervisor units).

## Conclusion

The premise in the dispatch spec ("BOSS=sonnet-high/WORKER=haiku-low
tiering already used by this dispatch pipeline") does not match the live
code: there is exactly one model/effort combination (`sonnet`/`high`) in use
across every real AI invocation site found, for both the boss/supervisor
role and the worker role. What *does* exist, real and already live, are two
unrelated "tier" concepts (scheduling-priority 0-4, and risk tier1/tier2) --
documented as such, not conflated with model selection. See
`state.json` `FACT-20260813-0007`/`FACT-20260813-0008` and
`dead_ends.json` `DEADEND-20260813-0002`.
