# Boss/worker dispatch tiering -- what's real today

Doc only -- no code change to any live dispatch/governor script. Written
for `task-20260813-035740-boss-worker-model-tier-orchestration--ad`
(addendum to P1 UMR-20260806-171945-5767, sibling of
`task-20260813-034138-token-efficiency-external-memory-system`).

This task's dispatch spec assumed a "BOSS=sonnet-high/WORKER=haiku-low"
model-cost tiering already exists in the live pipeline. It does not -- see
`sources/2026-08-13_boss-worker-model-tier-verification.md` for the full
grep evidence. This note documents what actually exists instead, and does
**not** create `boss.py`/`worker.py`/`orchestrator.py` or a new systemd
service: the live pipeline is `task-gateway.py` (submission/CLI front
door) + `resource_governor.py` (queue, priority, resource backpressure,
`umr_tasks` table) + `dispatch-owner-task.sh` / `dispatch_core.py`
(dispatch execution) + `worker-entrypoint.sh` / `doc-worker-entrypoint.sh`
/ `supervisor-entrypoint.sh` (the actual Claude Code invocations). Adding a
parallel framework on top would duplicate this, which the governing UMR's
zero-duplication rule forbids.

## 1. The two real "tier" concepts that exist

### a) Scheduling-priority tier (0-4) -- `resource_governor.py`

```python
TIER_MIN, TIER_MAX = 0, 4
DEFAULT_TIER = 2
```
(`/opt/veridian/scripts/resource_governor.py:68-69`)

This is a **queue-priority** value passed into `submit(task_spec, tier,
source_trigger)`: 0 is highest priority to dispatch next, 4 is lowest.
`umr_tasks` rows are ordered by this, with anti-starvation aging
(`max(0, tier - age_seconds // AGING_PROMOTION_INTERVAL_SECONDS)`, default
15-minute interval) so a low-priority item doesn't starve forever. It
governs **when** a unit gets dispatched, not **which model** runs it.

### b) Risk tier (tier1/tier2) -- `risk-tier.py` / `policy_decision.py`

`/opt/veridian/scripts/risk-tier.py` classifies a *completed diff* against
its base branch: tier1 = the server-side Superboss may merge autonomously,
tier2 = must hold for human sign-off. Classification logic lives in
`policy_decision.classify_risk_tier()` so it's one implementation, not a
copy. `supervisor-entrypoint.sh` calls this to decide whether to
auto-merge and to label the PR body ("Risk tier: $TIER"). This governs
**merge authority**, not model selection either.

## 2. What actually runs the AI, and at what model/effort

Every real Claude Code CLI invocation found under `/opt/veridian/scripts/`
uses the same model and effort, for both the worker role and the
boss/supervisor role:

| Script | Role | `--model` | `--effort` |
|---|---|---|---|
| `worker-entrypoint.sh:260` | worker (does the task) | `sonnet` | `high` |
| `doc-worker-entrypoint.sh:139` | doc worker | `sonnet` | `high` |
| `supervisor-entrypoint.sh:117` | Superboss (reviews the worker's diff) | `sonnet` | `high` |
| `master-decompose.py:105` | decomposition | `sonnet` | `high` |
| `gtm_check_ux_audit.py:137-138,528` | UX audit | `sonnet` | `high` |
| `dispatch-tick.py:746,909` (`PM_TRIAGE_CLAUDE_MODEL`, env-overridable) | PM triage | `sonnet` (default) | -- |

No script in `/opt/veridian/scripts/`, `/opt/veridian/systemd/`, or this
repo invokes `haiku` (or any other cheaper model) for any real dispatch
role. There is currently no live cost-tiering between boss and worker
invocations -- both cost the same per call.

## 3. If someone wants to actually build cost-tiering later

That is a separate, explicit implementation task against the real files
above (most likely: add a `--model`/`--effort` selection to
`worker-entrypoint.sh`/`doc-worker-entrypoint.sh` keyed off task risk or
resource-governor tier, with the Superboss/supervisor path staying on the
higher-capability model since it's the trust boundary). This note does not
propose specific values or make that change -- it only records the current,
verified state so a future task doesn't have to re-derive it, and doesn't
start from the false premise that the tiering already exists.

## 4. Prompt-caching-order note

Already covered by the sibling task's output --
`PROMPT_CACHING_ORDER_NOTE.md` in this same directory (static-first /
dynamic-last request structuring). Not duplicated here; see that file.
