# Phase 7 Planning: 72-Hour Retrospective (2026-07-27 -> 2026-07-30)

Status: ANALYSIS ONLY. No code, cron, systemd, schema, or config files were modified to
produce this document. Every claim below is tagged with the concrete evidence it rests on
(DB query, file path + mtime, `gh`/`git`/`systemctl` command output, or a live re-test I ran
myself during this session on 2026-07-30 between ~05:01 and ~05:20 UTC). Where I am inferring
rather than quoting a verified fact, it is labeled **[INFERENCE]**. Nothing below is asserted
as fact without a specific piece of evidence gathered in this pass.

Evidence base: SSH session to VERIDIAN-DEV (167.233.220.35) as `rajat`, live queries against
`/opt/veridian/ai-os/memory/superboss-register.sqlite` (80 tables; `instructions`=2,573 total
rows, 2,112 in the last 72h; `work_items`=640 total, 249 in 72h; `actions`=8,706 total, 1,472
in 72h; `umr_tasks`=107 total, 107 in 72h), plus `gh pr list`/`git log` on
compliance-tracker/projexa/claude-control, plus live `systemctl --user` and file-level checks.
Cutoff used for "last 72h" = 2026-07-27T00:00:00Z; current server time at start of this
analysis = 2026-07-30T05:01:41Z.

---

## PART 1 — Raw material from the 3 sources

### 1(a) superboss-register.sqlite, last 72h, categorized

Aggregate counts (verified via direct query, not estimated):
- `instructions`: 2,112 rows in window. `utm_source` breakdown: ai_agent=2020, owner=53,
  claude-agent=20, owner_chat=19.
- `work_items`: 249 rows. Status: pending=118, pending_review=66, open=54, DONE=5, closed=5,
  done=1.
- `actions`: 1,472 rows. Dominated by routine worker telemetry (periodic checkpoints=433,
  worker-started events, tier markers, exit codes) plus 31+23=54 rows of a **credit
  accountant** deterministically rejecting AI auto-fix spend with reason `"existing
  software/mechanism already covers this (system_index match) -- use it instead of spending
  AI credits"` — a real, working example of a deterministic-first spend gate. Also present:
  8 rows of `PRE-FLIGHT HARD STOP (tight_task_schema_violation)` and 7 rows of a supervisor
  refusing to guess a PR for branch `master` rather than risk operating on the wrong PR.
- `umr_tasks`: 107 rows, all in window. Status: killed=47, failed=40, completed=14,
  rejected_duplicate=4, running=2. task_kind includes a literal
  `'DROP TABLE umr_tasks; --'` string stored as inert data (see 1(c) security note below).
  source_trigger shows real adversarial/fuzz test rows (`adversarial-test-5/6`,
  `adversarial_test_4_injection_probe`) dated 2026-07-28.

Categorization of the real campaigns found (each below is a distinct `utm_campaign` value
with real rows, quoted from `raw_text`/`response_summary`):

**ANALYSIS/IMPLEMENTATION**
- `phase5-end-user-task-synthesis-2026-07-29` (INS-20260729-181826-f9f0): "PHASE 5
  GROUND-TRUTH SYNTHESIS ... 9 independent investigations completed ... KEY FINDING:
  END_USER_ENGINE does not exist as a named system (only inert placeholder columns added
  today); real software-first chat routing exists (policy gate -> 2 deterministic intents ->
  dialogue script -> LLM with es[calation])."
- `owner-veridian-perspective-evaluation-phase6-2026-07-30` (INS-20260730-041139-342c): gap
  evaluation from both Owner and system perspective, registered at
  `ai-os/GAP_EVALUATION_OWNER_AND_SYSTEM_PERSPECTIVE_2026-07-30.yaml` (verified present on
  disk, 19,484 bytes, mtime 2026-07-30 04:10).
- `master-index-central-entrypoint-confirmation-phase6-2026-07-30` (INS-20260730-040108-3928):
  answered "is MASTER_INDEX.yaml the central place" -> yes, but one of 4 complementary layers.
- `sap-report-buildnew-phase6-2026-07-30`: 4 real SAP-gap BUILD_NEW reports implemented
  (FI-AR-004 Dunning List / PR#636, FI-AP-005 Payment Proposal List / PR#637, SD-002 Billing
  Due List / PR#638, FI-AP-007 Subcontractor Retention Summary / PR#642).
- `utm-metadata-consolidation-phase6-2026-07-30`: evaluated 6 bespoke metadata mechanisms
  against the UTM standard; 1 genuine merge done (knowledge_engine.tags -> utm_term), 5
  correctly kept separate with reasons given per mechanism.
- VERIDIAN_CONSOLIDATED_COMPLETION (21 rows spanning 2026-07-29T05:07 to 2026-07-30T02:12):
  a real multi-phase master-task synthesis (Phase 0 through Stage 13) covering OWNER_ENGINE
  consolidation, browser/mini-VERIDIAN architecture plan, UTM standardization decision, unified
  search rollout (Stage 9), END_USER_ENGINE restricted-identity scaffolding (Stage 10), AI
  Dev Team dispatch-memory (Stage 12), and an AI usage billing engine (Stage 13/PR#635) — with
  a self-caught double-margining bug fixed before merge.

**AUDIT/IMPLEMENTATION**
- `cron-consolidation-reaudit-phase6-2026-07-30` (INS-20260730-041000-09c2): "Independently
  re-verified (not trusted from the prior session's summary): all 18 veridian-cron-* systemd
  --user timer/service pairs present, enabled, active ... crontab confirmed inert ... real gap
  found: EMERGENCY_STOP false-positive silently blocked 10/18 units execution for hours."
- `owner-engine-e2e-audit-2026-07-30` (INS-20260730-041910-7bbb): ran gateway.py
  `--mode owner-dispatch` for real, found two diverged copies of gateway.py exist (canonical
  `/opt/veridian/scripts/prompt_gateway/gateway.py` vs the `claude-control` repo copy),
  produced `/opt/veridian/ai-os/OWNER_ENGINE_E2E_AUDIT_2026-07-30.md` (verified present, 16,502
  bytes, mtime 04:18). Explicitly listed what's "Real/enforced" vs "Aspirational/not enforced"
  (pre-dispatch reuse check, during-work CI/policy monitoring, consistent post-hoc audit usage,
  documentation gate before close, unconditional output versioning, mechanical traceability —
  all named as NOT enforced).
- `product-repo-duplicate-pr-dispatch-dedup-2026-07-29`: root-caused projexa PR #64/#65/#66
  and compliance-tracker #620/#625, #621/#623 duplicate PRs to the same work being submitted
  under different `task_identity` strings.
- **Formal audit pipeline is stale**: `audit_events`, `audit_runs`, `audit_orchestration_runs`,
  `audit_master_reports`, `audit_findings` all show `MAX(ts)` = **2026-07-25T06:05:58Z** — zero
  rows in the last 72h across all five tables. Every "audit" described above (cron re-audit,
  OWNER_ENGINE e2e audit, gap evaluation) was logged as an `instructions` row from an ad-hoc
  session, not a run of the actual automated audit_* pipeline. `directive_compliance_runs` is
  the one audit-adjacent table that IS live (70 rows in 72h, latest 2026-07-30T04:54:31Z).

**ISSUES-ENCOUNTERED/FIX**
- `emergency-stop-diskio-rootcause-fix-phase6-2026-07-30` (INS-20260730-043122-260a):
  "EMERGENCY_STOP disk_io false-positive: root-caused as a real formula bug (raw
  sector-throughput vs an arbitrary 200MB/s constant, plus partition double-counting) ...
  verified against real `sar -d %util` for all 3 trip timestamps (26.7%/61.7%/62.5% real vs
  100.0% reported each time). Fixed resource_governor.py disk_io_percent()/
  read_disk_sectors() to use /proc/diskstats field 13 (io_ticks)."
- `infra-fixes-phase6-2026-07-30`: Bug 1 (app_runtime DB password mismatch) — root-caused,
  explicitly **not fixed** ("password recorded in memory/veridian_db_credentials_rotated
  _2026-07-06.md ALSO fails now ... rotated again since 2026-07-06 without being recorded
  anywhere"). Bug 2 (product_branches schema drift) — investigated and found to be a
  misdiagnosis, no real bug.
- `owner-engine-layered-router-fix-phase6-2026-07-30` (INS-20260730-045322-ddf9): "Root cause
  of gateway_output_20260730.json (QUERY/0.3263/lifecycle none): no GOVERNANCE category
  existed and no lifecycle-route branch existed for policy/governance statements." Fixed by
  adding `engine/layer0_router.py` ahead of `ChatClassifier.classify()`.
- Security/adversarial test suite on 2026-07-28 (`umr_tasks` source_trigger
  adversarial-test-4/5/6): SQL-injection strings, a 500,014-character oversized `task_identity`
  payload, and duplicate-submission probes were all fed to the live submit path. All landed as
  inert stored strings (table intact, 107 rows, no corruption) with `status IN
  ('failed','rejected_duplicate')` — real evidence the parametrized-query and dedup paths hold
  under adversarial input, not just well-formed input.
- `pr-ci-fixes-phase6-2026-07-30`: fixed real CI failures on PR#636/637/638 without merging.

Several rows genuinely span two categories (e.g. the cron re-audit is AUDIT that surfaced a
new ISSUE — the EMERGENCY_STOP false-positive blocking 10/18 units — which was then FIXED
separately in a distinct campaign the same morning).

### 1(b) Known threads cross-referenced against the DB

Every thread the Owner listed as "real known major threads" was found with a matching,
dated, non-empty `utm_campaign` in `instructions`: Phase 5 synthesis
(`phase5-end-user-task-synthesis-2026-07-29`), OOM-incident-era work (found via a `raw_text`
keyword search, e.g. INS-20260728-192322-a829 referencing "fail2ban lockout, OOM incident"),
cron consolidation (`cron-consolidation-phase6-2026-07-29` +
`cron-consolidation-reaudit-phase6-2026-07-30`), the EMERGENCY_STOP disk_io fix
(`emergency-stop-diskio-rootcause-fix-phase6-2026-07-30`), UTM consolidation
(`utm-metadata-consolidation-phase6-2026-07-30`), MASTER_INDEX self-regen + central-entrypoint
confirmation (`master-index-scoped-apply-phase6-2026-07-30` +
`master-index-central-entrypoint-confirmation-phase6-2026-07-30`), the OWNER_ENGINE Layer-0
router fix (`owner-engine-layered-router-fix-phase6-2026-07-30` +
`owner-engine-layer0-e2e-retest-2026-07-30`), the SAP-reports build effort
(`sap-report-buildnew-phase6-2026-07-30`, `zai-sap-queue-correction-phase6-2026-07-30`), and
duplicate-PR dispatch fixes (`product-repo-duplicate-pr-dispatch-dedup-2026-07-29`, plus PR
#117 on claude-control "UTM phase 6" and PR #110 "Add Server Resource Governor" from `git log`).

**Not on the Owner's list, found independently**: the `VERIDIAN_CONSOLIDATED_COMPLETION`
master-task chain (Phase 0-3, Stages 0a-13) is a much larger structure than any single named
item on the list — it appears to be the umbrella that several of the named threads (UTM
decision, unified search, END_USER_ENGINE restricted-identity scaffolding, AI Dev Team
dispatch-memory, AI usage billing engine) were executed under. Also not listed: the formal
audit_* pipeline's 5-day staleness (a real gap, detailed above), and the adversarial/injection
test suite from 2026-07-28.

### 1(c) Other-session / parallel-activity artifacts

- `utm_source='ai_agent'` accounts for 2,020 of 2,112 instructions in the window — far more
  than `claude-agent` (20). **[INFERENCE, moderate confidence]**: this is consistent with the
  standing autonomous worker/dispatch loop (`auto-worker-task-log`, `worker-entrypoint-main-
  invocation`, `supervisor-entrypoint-review-invocation` — 1,058+136+131 = 1,325 of 1,472
  `actions` rows) running continuously and independently of any interactive Claude Code
  session, rather than evidence of a specific *other* interactive session. I did not find a
  distinct utm_source value that clearly indicates a second interactive Claude Code CLI
  session (e.g. a different `claude-agent`-like tag) — the only two "assistant-authored"
  looking sources present are `claude-agent` (20 rows, all matching this retrospective's known
  threads) and `owner_chat` (19 rows, a different logging path used for a same continuous
  Owner<->assistant conversation, not a separate session by itself).
- `gh pr list` on **compliance-tracker** (exact count, re-pulled with `--limit 100` to avoid
  truncation, confirmed complete because the oldest PR in that pull, 2026-07-21, predates the
  72h cutoff): **61 PRs created since 2026-07-27, of which 29 are MERGED** — real evidence of
  heavy automated-worker PR volume (matches the actions-table worker telemetry above), not
  necessarily "other Claude Code sessions" in the interactive sense. (Note: an earlier,
  `--limit 50` pull of this same repo undercounted this at "28 created / 3 merged" because the
  50-row page was fully saturated with in-window PRs and cut off mid-window — corrected here
  with the completeness check applied.)
- `gh pr list` on **projexa** (`--limit 30`, not saturated — 16 of 30 rows recent, confirming
  completeness): 16 PRs since 2026-07-27, 9 merged (#51,52,54,56,57,59,60,61,62), including
  "Wire full VERIDIAN module chain into PROJEXA's chat console" (#59, merged) and 3 repeated
  "Resolve fresh conflict on PR #58" attempts (#64/#65/#66, all still OPEN as of this check) —
  this is the concrete artifact behind the "duplicate-PR-dispatch" thread.
- `gh pr list` on **claude-control** (`--limit 50`, not saturated — oldest pulled row is
  2026-07-25, before cutoff): 16 PRs since 2026-07-27, 9 merged, including PR #117 "UTM phase
  6: merge knowledge_engine.tags into utm_term" (MERGED 2026-07-30T04:06:44Z), PR #110 "Add
  Server Resource Governor" (MERGED 2026-07-27), PR #112 "phase_9_gateway_knowledge_sync
  _infrastructure" (MERGED 2026-07-27).
- `git log --all --since=2026-07-27` on claude-control shows commits under two author-name
  spellings ("Rajat Agarwal" via automated commits vs "RAJAT AGARWAL" on a couple of manually
  authored ones), plus repeated "Auto-sync N server task(s) to master controller" commits —
  real evidence of an automated sync process running independently on its own cadence, most
  recently 2026-07-30T05:05:26Z, essentially concurrent with this analysis.
- Recent file mtimes in `/opt/veridian/ai-os/` (top level, last 72h) surfaced items not
  otherwise covered above: `DEDUP_MISMATCH_MANUAL_REVIEW_2026-07-27.yaml`,
  `PENDING_OWNER_REVIEW_2026-07-28.md` (referenced by the Layer0 GOVERNANCE test row summary,
  though that summary cites the filename as `PENDING_OWNER_REVIEW.md` without the date suffix
  — a small, real naming inconsistency worth flagging), and
  `MASTER_INDEX.yaml.bak-2026-07-30-before-central-entrypoint-pass` (a manual backup-file
  convention, see Part 3).

---

## PART 2 — Distilled analysis: the one root problem

Reading analysis + audit + issues together, the same root problem recurs in three disguises:

**"Silos, no single source of truth" (Owner's own words, verbatim in
INS-20260730-045031-b663) shows up as:**
1. *An analysis finding*: Phase 5 synthesis concluding END_USER_ENGINE "does not exist as a
   named system," and the owner-perspective gap evaluation noting SAP-report PRs "exist but
   none are merge-ready" with no single tracker showing that.
2. *An audit finding*: MASTER_INDEX.yaml confirmed as only one of 4 complementary layers (not
   the sole source), and the OWNER_ENGINE e2e audit's direct discovery that **two live copies
   of gateway.py exist and have diverged** — the canonical `/opt/veridian/scripts/
   prompt_gateway/gateway.py` is verifiably newer than the `claude-control` repo's copy (this
   session re-confirmed via `diff -q`, exit code 1 = files differ, right now).
3. *An issues-encountered/fix finding*: the credentials-drift bug (app_runtime DB password
   rotated a second time "without being recorded anywhere," per INS-20260729-205312-3c1a) is
   the same silo problem in a different artifact class (a secret instead of a doc or a script).

The mechanism producing all three is the same: **real work has been happening in at least
three different places that don't automatically reconcile with each other** — (a) live,
non-git-tracked files on disk under `/opt/veridian/scripts/` and `/opt/veridian/ai-os/`
(version-"controlled" only by ad-hoc `.bak-predeploy-*`/`.pre-*-backup-*` filename suffixes,
of which 7 exist for `gateway.py` alone as of this check), (b) the `superboss-register.sqlite`
memory DB (instructions/work_items/actions/umr_tasks — the layer this whole retrospective is
built from), and (c) actual git repos (claude-control, compliance-tracker, projexa) where the
formal PR/CI/audit-check gates live. A fix applied to (a) does not automatically appear in
(c); an audit described in (b) does not automatically populate the formal `audit_*` tables
that (per Part 1a) have been silent for 5 days. Every "fix" this week has been a *manual*
reconciliation across these three layers by a diligent agent, not a structural guarantee that
they stay in sync.

---

## PART 3 — Self-audit of Part 2, with fresh direct re-verification

Re-reading Part 2: it correctly connects the gateway.py-drift finding to the credentials-drift
finding as instances of the same silo problem; I do not think it overstates the "3 layers"
framing — it is grounded in the diff/mtime evidence below. One thing Part 2 could have
connected but under-weighted: the `audit_*` pipeline staleness (5 days) is *itself* another
instance of the same root problem — a fourth would-be single source of truth that nobody has
been writing to, while ad-hoc audits happened elsewhere. Adding that explicitly here.

Fresh, direct re-verification performed in this session (not trusting any prior report):

| Fix claimed earlier today | Re-verified right now | Evidence |
|---|---|---|
| Cron consolidation, 18/18 systemd units | **STILL TRUE** | `systemctl --user list-unit-files 'veridian-cron-*.timer'` shows exactly 18 timers, all `enabled enabled`. `list-timers --all` shows real, recent "last triggered" times for each (e.g. dispatch-tick 4m28s ago, file-inventory 1m18s ago, sync-controller-back 2m13s ago, all relative to ~2026-07-30T05:08 UTC) — they are actively firing, not just enabled-on-paper. |
| EMERGENCY_STOP disk_io formula bug | **STILL FIXED, currently clear** | `grep` of the live `resource_governor.py` shows `read_disk_io_ticks()` / `disk_io_percent()` implemented against `/proc/diskstats` field 13 (io_ticks), with an explicit code comment dated `ROOT-CAUSE-2026-07-30`. The sentinel file itself (`EMERGENCY_STOP_PATH`, resolved from the script's own `LOCKS_DIR` constant) does **not** currently exist on disk — the governor is not tripped right now. |
| UTM consolidation (knowledge_engine.tags -> utm_term) | **TRUE, but nuanced** | `register_knowledge()`'s live source (lines ~1650-1658) shows `utm_term` is auto-derived (`",".join(tags_list)`) from the caller's single `--tags` input — there is genuinely only one input path now, not two independently-suppliable fields. However the `tags` **column itself was not dropped**: all 359 `knowledge_engine` rows still carry both a legacy JSON-array `tags` value and the derived comma-joined `utm_term` — this is an additive/backward-compatible merge (both stored) not a schema-level dedup. Confirmed merged via claude-control PR #117 (merged 2026-07-30T04:06:44Z). |
| MASTER_INDEX.yaml self-regeneration | **Real script exists; NOT wired into cron** | `regenerate_master_index.py` exists (30,049 bytes, mtime 2026-07-29 18:52) and `MASTER_INDEX.yaml` itself was regenerated recently (mtime 2026-07-30 04:09, matching PR #640 "close 7 real coverage gaps", merged 04:18:30). But checking the live list of 18 cron timers: **none of them is a master-index regeneration job.** Regeneration today was a manual, session-triggered run, not an automated recurring one. |
| OWNER_ENGINE gateway.py Layer-0 router fix | **STILL WORKING, re-tested live just now** | I piped a fresh governance-shaped test string ("Owner policy note: from now on every new module must register its capability in capability_registry before deployment") into the live `gateway.py --mode stdin` at 2026-07-30T05:16:24Z. Real output: `Classification: GOVERNANCE (confidence: 1.0, intent: UNKNOWN)`, Layer0 matched. This is a fresh result generated by me, not a re-read of the earlier 9-row retest. |
| Duplicate-PR-dispatch fixes | **Guard code confirmed live; underlying repo state still shows the problem** | `resource_governor.py` contains a real `find_active_umr_by_identity()`-based dedup guard (confirmed: an adversarial dedup-probe row got `status='rejected_duplicate'` on 2026-07-28). But `gh pr list` on projexa **right now** still shows PR #64/#65/#66 all open, all titled "Resolve fresh conflict on PR #58" — the guard prevents *new* duplicate dispatch going forward, it has not retroactively cleaned up the 3 existing duplicate PRs from before the fix. |

**A concrete drift caught in this pass, not present in any prior report**: the
`pr-ci-fixes-phase6-2026-07-30` campaign (logged 2026-07-30T04:46:01Z) states "PR636 PASS,
PR637 PASS, PR638 PASS — all 3 genuinely mergeable, **none merged**." Re-querying `gh pr view
636` right now shows `state=MERGED`, `mergedAt=2026-07-30T04:48:46Z` — **2 minutes 45 seconds
after that summary was written**, PR #636 was in fact merged, with all 19 status checks
(Lint, audit-check, Terminology Guardrail Check, E2E Tests, etc.) SUCCESS. PR #637 and #638
remain OPEN as of this check. This is exactly the kind of "may have drifted since" the Owner
asked me to check for — the earlier report was accurate at the moment it was written and is
now stale in one specific, verifiable detail.

**Another crack found only by direct re-verification, not claimed by any prior report**: the
canonical `gateway.py` / new `layer0_router.py` fix that was "deployed and E2E verified" today
exists **only as a live file on disk** at `/opt/veridian/scripts/prompt_gateway/`. It is not
present anywhere in the `claude-control` git repository (`find` for `layer0_router.py` inside
that repo returns nothing; `git log --all --oneline -i --grep='layer0'` returns nothing;
`git status` in that repo is clean). `/opt/veridian/scripts` is a real, independent directory,
not a symlink into any git repo (`readlink -f` resolves to itself). Version control for this
canonical enforcement script is currently a manual `.bak-predeploy-<timestamp>` /
`.pre-<stage>-backup-<date>` filename convention (7 backup copies of `gateway.py` alone were
found sitting alongside the live file). This means: no code review happened for this fix, and
if the server's `/opt/veridian/scripts` directory were ever lost or rebuilt from git, this fix
would not be recoverable from any repository.

---

## PART 4 — Does deterministic-first + documented + dedup-checked + reusable hold end-to-end?

**Owner -> system**: Real, and re-verified live in this pass (see table above — GOVERNANCE
input correctly routed with confidence 1.0 just now). Caveat found in Part 3: the fix itself
sits outside version control, so "real" today carries an operational fragility that wasn't
visible before this check.

**AI acting on behalf of the Owner (dispatching new work)**: **Not a structural gate** —
confirmed by the OWNER_ENGINE_E2E_AUDIT_2026-07-30.md itself (which I verified exists on disk,
16,502 bytes), whose own findings list "pre-dispatch reuse check" and "consistent post-hoc
audit usage" under "Aspirational/not enforced," not "Real/enforced." The credit-accountant
spend-rejection rows in `actions` (54 rows, reason: "existing software/mechanism already
covers this... use it instead of spending AI credits") ARE a real deterministic gate — but it
fires only at the *AI-auto-fix-spend* decision point, after a worker is already dispatched and
attempting a fix; it is not a gate that prevents a duplicate task from being dispatched in the
first place (that guard — `find_active_umr_by_identity` — exists and works, per Part 3, but
only within `resource_governor.py`'s own submit path, and does not appear to prevent the kind
of cross-repo duplicate PR seen in projexa #64/#65/#66, which arose from two *different*
`task_identity` strings referring to the same real underlying work — a dedup check keyed on
identity string equality cannot catch that). Today's "zero duplication" enforcement for
AI-for-Owner is overwhelmingly the product of careful agent prompting and self-audit
discipline (the VERIDIAN_CONSOLIDATED_COMPLETION chain's "3 independent fresh-context
adversarial audits" pattern, repeated across multiple stages) — not a software gate that
exists independent of the agent choosing to run it.

**End_user**: chat-service.ts's layered pipeline was described in Part 1 findings
(policy gate -> 2 deterministic intents -> dialogue script -> LLM with escalation) but I did
not re-verify chat-service.ts directly in this pass (out of scope of the 4 named
DB tables and the explicit re-verification list in the task) — treating the "already
confirmed working" framing as carried over from prior verified sessions, **not independently
re-checked by me today**; flagging this as unverified-by-me rather than re-asserting it as
fact. PROJEXA's own path: `gh pr list` evidence in Part 1(c) shows PROJEXA's real recent PRs
are CRUD/module features (Permits/Drawings/Documents, Resource management, dashboard
drill-down, Work Progress Report, PWA offline sync) — consistent with "form/CRUD-only, not
AI-routed" — this is a **different category entirely**: PROJEXA is a product built *on*
VERIDIAN infrastructure via API, not itself running the OWNER_ENGINE/END_USER_ENGINE chat
pipeline for its own end users, based on the PR titles alone. **[INFERENCE]**: I did not
locate a PROJEXA-side chat/AI-routing PR or file in this pass to confirm or deny AI-routing
at the point of end-user interaction; this verdict rests on PR-title-level evidence, not a
code read.

**AI-for-end-user**: Not independently re-checked in this pass (capability-audit-service.ts
was not part of the 4 DB tables or the explicit Part-3 re-verification list); carrying forward
"dead-ends at a human-reviewed advisory" as **unverified-by-me-today**, not confirmed fact.

---

## Phase 7 — concrete, scoped gap list (planning only, nothing implemented)

1. **Put `/opt/veridian/scripts/prompt_gateway/` (and any other canonical live-enforcement
   script directory) under real git version control**, replacing the `.bak-predeploy-*`
   filename convention. Scope: `gateway.py`, `layer0_router.py`, `resource_governor.py`,
   `regenerate_master_index.py`, `superboss-register.py`. Concrete acceptance test: `git log`
   in whichever repo hosts them shows a commit for today's Layer-0 router change; `diff -q`
   between the live file and the repo's tracked copy returns no difference.

2. **Wire `regenerate_master_index.py` into the 18-unit cron/systemd set** (or explicitly
   document why it's deliberately manual-only) — right now it is a real script that ran once
   today by hand. Acceptance test: `systemctl --user list-timers` shows a master-index-regen
   timer with a real recent last-run time.

3. **Add a pre-dispatch reuse/duplicate check that is keyed on more than exact
   `task_identity` string equality** — the projexa #64/#65/#66 case shows two different
   identity strings pointing at the same real underlying work slipping past the existing
   `find_active_umr_by_identity()` guard. Acceptance test: feed two differently-worded task
   specs describing the same target PR/issue and confirm the second is rejected or flagged,
   not silently dispatched.

4. **Give the formal `audit_*` pipeline (audit_events/audit_runs/audit_orchestration_runs/
   audit_master_reports/audit_findings) a real reason to run again**, or consciously retire it
   in favor of whatever mechanism (ad-hoc `instructions` rows + manual `.md`/`.yaml` reports)
   has actually been carrying the audit workload for the last 5 days. Leaving it silently
   stale while calling other things "audits" is itself a silo. Acceptance test: either a new
   `audit_runs` row appears within N days, or a documented decision to deprecate it is
   registered in `knowledge_engine`.

5. **Retroactively reconcile the 3 known-existing duplicate-PR clusters** (projexa
   #64/#65/#66; compliance-tracker #620/#625 and #621/#623) now that the forward-looking guard
   exists — today's fix is prevention-only, the existing duplicates are still open. Acceptance
   test: `gh pr list` on each repo shows the clusters collapsed to one open PR each, others
   closed with a cross-reference.

6. **Decide and document what "AI acting on behalf of the Owner" needs as a structural
   pre-dispatch gate**, distinct from the existing post-dispatch credit-accountant spend
   check. Today's evidence (Part 4) shows the *only* real software gate at that stage is
   an after-the-fact "don't spend more AI credits on this, a system_index match already
   covers it" rejection — there is no equivalent gate *before* a new task is accepted into
   the queue. Acceptance test: a concrete design doc (not code) naming what such a gate would
   check and where in the dispatch path it would sit.

7. **Correct the small MASTER_INDEX-adjacent doc-naming drift found in passing**: the
   Layer-0 GOVERNANCE test row (INS-20260730-045031-e81b) references
   `PENDING_OWNER_REVIEW.md`, but the real file on disk is
   `PENDING_OWNER_REVIEW_2026-07-28.md`. Small, but exactly the class of drift this whole
   initiative is trying to eliminate.

8. **Independently verify (not carry forward) the chat-service.ts end-user pipeline and
   capability-audit-service.ts escalation-loop claims** from prior sessions — Part 4 of this
   retrospective explicitly could not re-confirm either in this pass; they are outside the
   scope of what I checked today (the 4 named DB tables + the Part-3 fix list) and should not
   be treated as re-verified just because this document exists.

---

*Document produced 2026-07-30 by a Claude Code CLI analysis-only session. All evidence above
was gathered live during this session via SSH to VERIDIAN-DEV; no file under
`/opt/veridian` other than this document itself was created or modified as part of producing
this analysis (one live test invocation of `gateway.py --mode stdin` was run, which writes an
`instructions` row as its normal, designed behavior — the same kind of read/test call the
`owner-engine-layer0-e2e-retest-2026-07-30` campaign itself performed nine times earlier
today).*
