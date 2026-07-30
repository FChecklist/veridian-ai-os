# OWNER_ENGINE End-to-End Audit — 2026-07-30

Real, evidence-based audit run against the live VERIDIAN-DEV server (167.233.220.35).
No claim below is asserted without a file:line, command output, or DB query backing it.
Where something is aspirational rather than enforced, it is labeled NOT ENFORCED explicitly.

## PART 1 — Real gateway.py invocation (the actual deliverable)

Two live copies of `gateway.py` exist on disk:
- `/opt/veridian/scripts/prompt_gateway/gateway.py` (47315 bytes, mtime 2026-07-29 11:23) — CANONICAL, live path
- `/opt/veridian/repos/claude-control/scripts/prompt_gateway/gateway.py` (42415 bytes, mtime 2026-07-26 12:00) — STALE repo copy, missing the Stage-2 resource_governor rerouting block (diff confirmed, 100+ line delta). `/opt/veridian/scripts` is NOT a symlink into the repo and is NOT itself a git repository (`git status` → "not a git repository"). This divergence is itself a live instance of the exact silo problem the Owner described.
- A third copy exists at `/opt/veridian/workspace/engine-inventory-reverify-20260727/scripts/prompt_gateway/gateway.py` (a workspace snapshot, not canonical).

Real CLI surface (`python3 gateway.py --help`):
```
--mode {stdin,file,interactive,pipe,init,owner-dispatch}
--input INPUT --session SESSION --output OUTPUT --json-only --base-dir --verbose --repo
```
`owner-dispatch` is documented as "the single entrypoint that also calls task-gateway.py submit/start/status directly when the classified message is a task-lifecycle request."

**Real command run:**
```
cd /opt/veridian/scripts/prompt_gateway && \
python3 gateway.py --mode owner-dispatch --session owner-engine-e2e-audit-2026-07-30 \
  --output /tmp/gateway_output_20260730.json --verbose < /tmp/owner_observation_20260730.txt
```
(Note: `--mode owner-dispatch` ignores `--input` entirely — confirmed at gateway.py:885-888, it only reads `sys.stdin`. The Owner's raw observation text was piped via stdin.)

**Real output (`/tmp/gateway_output_20260730.json`, full contents):**
```json
{
  "chat_id": "VD-20260730040756-0001",
  "session_id": "owner-engine-e2e-audit-2026-07-30",
  "classification": { "category": "QUERY", "intent": "QUERY", "confidence": 0.3263 },
  "processing": {
    "original_chars": 965, "cleaned_chars": 963, "noise_reduction_pct": 0.2,
    "machine_prompt": "QUERY:ever OWNER told anything, you started again, made new work, new documents...",
    "token_reduction_pct": 31.3, "processing_time_ms": 4.0
  },
  "entities": [ /* 20 CODE_REF entries, ALL of them ALL-CAPS words like OWNER/We/AND/YOU/HAVE/GOING/FORWARD/ANY/IS/BY/AI/OWNER_ENGINE, plus one MEASUREMENT "30 days" */ ],
  "lifecycle_dispatch": { "action": "none", "task_id": null, "result": null }
}
```

**This result is itself the single most important finding of this audit.** The gateway classified the Owner's own governance directive as a low-confidence (0.3263) `QUERY`, extracted no meaningful entities (just every ALL-CAPS word in the text, because entity extraction is a naive caps-heuristic — confirmed no NLP/semantic extraction, just regex-shaped matching), and **dispatched nothing** (`lifecycle_dispatch.action: "none"`, `task_id: null`). No task was created, no capability_registry/wiring_registry check ran, nothing was persisted anywhere durable. The exact category of instruction the Owner is most concerned about — a meta/process directive rather than a "fix X" task — is precisely the category this pipeline currently fails to route into any tracked, auditable unit of work.

## PART 2 — Six-question audit

### Q1. Before work: is there a real "check existing first" gate?

**NOT ENFORCED in the gateway→dispatch path.** Traced the real call chain:
`gateway.py route_and_dispatch()` (gateway.py:487) → `dispatch_to_task_lifecycle()` → real `task-gateway.py submit/start` subprocess calls (task-gateway.py, `PROMPT_GATEWAY`/`POSTFLIGHT` constants at lines 43-44) → `task-gateway.py`'s `start` action (Stage-2, task-20260729) now routes through `resource_governor.py --submit` instead of calling its own start directly (confirmed via diff between the two gateway.py copies, lines ~105-118 and ~265-273 of the canonical copy).

Grepped every file in this chain for `capability_registry`/`wiring_registry`/`knowledge_engine`/`system_index`: **zero hits in `gateway.py`, `task-gateway.py`, or `dispatch_core.py`.** The only genuine consumer of `capability_registry` as a pre-work reuse check is `plan_generator.py` (docstring: "resolves EACH step against Phase 1's live capability_registry") — but `grep -rl plan_generator /opt/veridian/scripts/*.py` (excluding itself) returns **zero callers**. It is a real, well-designed, completely orphaned tool — not wired into the dispatch path at all. `automation_rule_engine.py` does query `capability_registry` (line 132: `SELECT capability_name FROM capability_registry WHERE ...`), but it's only called by `document_engine.py`, `intent_engine.py`, `learning_engine.py`, `notification_engine.py`, `webhook_receiver.py` — none of which sit in the owner-dispatch→task-gateway.py→resource_governor.py submit path.

`task-gateway.py` does reference `knowledge_engine`, but only via `reverify_touched_knowledge_engine_rows()` (line 571) — called from `cmd_close` (line 722), i.e. **after** work is done, to reconcile which knowledge_engine rows were touched by the diff. This is post-hoc bookkeeping, not a pre-dispatch "does this already exist" check.

**Conclusion: the "check existing before creating new" step depends entirely on whichever AI/agent remembers to do it manually. There is no software gate.**

### Q2. During work: live monitoring for policy violations (new cron/.py/.yaml vs edit-existing)?

Partially real, but narrow and gate-based rather than continuous:
- `tight_task_validation.py` validates a task's `prompt.txt` at submit time — it checks SUCCESS_CRITERIA contains a runnable command (`check_success_criteria_has_runnable_command`) and has NLP-ish contradiction detection for prohibitive clauses like "adds no cron entries" vs the rest of the prompt (`detect_field_contradiction`, lines 274+). This validates internal consistency of what the task *claims* it will/won't do — it does not diff the filesystem before/after to verify the claim was true.
- `postflight_audit_gate.py` runs at close time (see Q3) and only checks whatever `--audit-cmd` the task author wrote at plan time. Nothing forces that command to include a "no new top-level .py/.yaml/cron entry" check — it's opt-in per task, not a blanket policy.
- No live/continuous watcher process was found (no filesystem watcher, no cron-diff daemon) that monitors an in-progress task.
- CI-level equivalents: **confirmed zero.** `/opt/veridian/scripts` and `/opt/veridian/ai-os` are not git repositories at all (no `.git`), so no CI can trigger on them by construction. Checked every `.github/workflows/*.yml` across all cloned repos (`claude-control`, `compliance-tracker`, `compliance-tracker-projexa-records-wt`): `mandatory-audit-check.yml`, `ci.yml`, `sentinel.yml`, `codeql.yml` etc. all exist **only in compliance-tracker** (the product repo) and none of them reference `opt/veridian/scripts` or `opt/veridian/ai-os` paths. `claude-control`'s only workflow is `claude.yml` (the Claude Code GH Action itself, not an audit gate). **The Owner-side infra tree has no CI-equivalent gate at all today.**

### Q3. After work: real independent audit, or self-certification?

**Real for the narrow case where it's actually invoked; NOT consistently invoked for recent work.**

`task-gateway.py cmd_close` (line ~648 on) is a genuinely well-designed anti-self-cert gate:
- It requires `--audit-cmd` to appear **verbatim** inside the task's own pre-written `SUCCESS_CRITERIA` (extracted from `prompt.txt` at *plan/dispatch* time), explicitly rejecting a command authored fresh at close time ("self-certification is exactly what this rule prevents" — code comment, task-gateway.py ~line 660-664).
- It then actually **executes** that command via `postflight_audit_gate.py` (`subprocess.run(["bash","-c",args.audit_cmd], ...)`, postflight_audit_gate.py:170) and the real exit code decides `verdict`. If `verdict != "DONE"`, `cmd_close` prints the failure and `sys.exit(1)` — it never reaches the "closed" status write to `superboss-register.py log-work`.

This is real, not aspirational — it independently re-executes a predefined check rather than trusting the AI's claim.

**But the evidence shows it is not being used consistently.** Queried `superboss-register.sqlite` (`/opt/veridian/ai-os/memory/superboss-register.sqlite`, 80 tables total) directly:
- `task_audits` (the table `postflight_audit_gate.py` and only it, plus 4 other read-side scripts, write to): **16 rows total, most recent row `AUD-20260727-122244-7dedec` at 2026-07-27T12:22:45Z.** Zero rows from 2026-07-28, -29, or -30, despite substantial work reportedly landing in that window (Stage-2 resource_governor rerouting task-20260729, dedup-masking fix PR #102, PR #117 UTM consolidation, etc.). **Either that work was closed without going through the enforced `cmd_close`/`postflight_audit_gate.py` gate, or it hasn't been formally closed at all — in both cases, the one table with genuine independent verification has a 3-day gap covering exactly the work this audit was asked to trace.**
- `audit_runs` (162 rows), `audit_findings` (16672 rows), `audit_master_reports` (2 rows, both timestamped 2026-07-25), `audit_orchestration_runs` (2 rows, both 2026-07-25): this is a **separate system** — a broad security/compliance static-analysis sweep (standard/clause-cited findings), run twice total, last run 5 days before this audit. It is not a per-task "was this specific Owner-dispatched unit of work 100% completed" check; it's periodic code/compliance scanning, unrelated to the postflight gate.

**Conclusion: the completion-audit mechanism is real and non-trivial where used, but usage has lapsed for the most recent ~3 days of work, meaning recent "done" claims are effectively self-reported, not gate-verified, as of this writing.**

### Q4. Documentation: real enforced step, or "AI is supposed to remember"?

**NOT enforced as a gate.** `gateway.py` never calls `log_instruction()` or `register_knowledge()` anywhere in its source (confirmed via grep — zero hits). `cmd_close`'s only hard requirement is the postflight audit verdict; nothing in the close path requires a `knowledge_engine` or `instructions` row to exist before a task can reach `closed` status (confirmed by reading the code around `cmd_close`: after `verdict == "DONE"`, it proceeds straight to `SUPERBOSS log-work --status closed` with no documentation-presence check gating that call). Documentation happens if and only if the acting AI chooses to call `superboss-register.py log-instruction` / `register-knowledge` itself — exactly the "AI is supposed to remember" pattern the Owner flagged.

One partial, real mitigation observed empirically: recently-superseded docs in `/opt/veridian/ai-os/` are renamed rather than deleted, e.g. `completion_of_pending_tasks.md.superseded-by-INS-20260729-050130-0111` — a real (if manual, suffix-based) "don't destroy, point to what superseded it" convention. That's evidence of *discipline in practice for some files*, not of a *software-enforced gate for all files*.

### Q5. Versioning: are gateway.py's own YAML/JSON outputs versioned, or lost?

**Conditionally real, and this audit's own Part-1 run is a live demonstration of the gap.** `register-knowledge`'s CLI (`superboss-register.py register-knowledge --help`) requires `--path` pointing at a real file (content_hash + exists_on_disk are computed from a live read, never guessed — confirmed in `register_knowledge()`, superboss-register.py:1605-1613) plus `--artifact-type {canonical,derived}`. So *if* a gateway.py run gets classified as an actionable task and flows through `task-gateway.py cmd_submit`, its `machine_prompt`/`final_output` is written into a durable, versioned `prompt.txt`/`task.yaml` under `/opt/veridian/ai-os/tasks/{task_id}/` (confirmed at task-gateway.py ~line 748-751).

But Part 1's real run classified as `QUERY` with `lifecycle_dispatch.action: "none"` — **no task was created, so nothing was persisted anywhere durable.** `/tmp/gateway_output_20260730.json` would be gone on next reboot/tmp-clean if this audit hadn't manually scp'd it off-box. Gateway.py's own output has zero built-in persistence for anything not classified as a dispatchable task — which is exactly the class of input (a governance/process observation) this whole audit is about.

### Q6. Traceability: one real example, traced backward, honestly.

Picked the **UTM metadata consolidation (Phase 6)** work, real and same-day: `knowledge_engine` row `KE-20260730-041039-5888`, `artifact_path = /opt/veridian/ai-os/UTM_METADATA_CONSOLIDATION_PHASE6_2026-07-30.md`, `metadata_json` contains `"pr": "https://github.com/FChecklist/claude-control/pull/117", "merged": true`.

Trace attempt:
1. **Code → doc**: PR #117 → `UTM_METADATA_CONSOLIDATION_PHASE6_2026-07-30.md` — linked via the `knowledge_engine` row's `metadata_json.pr` field. Works.
2. **Doc → instruction**: the `knowledge_engine` row's own `entity_relationships` column is `"[]"` — **empty, no structured link to any instruction row**, even though the CLI supports `--relationships` for exactly this. Had to fall back to matching `utm_campaign = "utm-metadata-consolidation-phase6-2026-07-30"` by hand against the `instructions` table. Found `INS-20260730-041057-d48f`, timestamped **18 seconds after** the knowledge_engine row — i.e. this is the acting AI's own retrospective "here's what I did" log (`utm_source: claude-agent`), not an upstream cause.
3. **Instruction → real Owner request**: no earlier `utm_source='owner'` row shares this exact campaign slug. Had to text-search `raw_text LIKE '%UTM%'` around 2026-07-29 by hand and found two `utm_source='owner_chat'` rows from the prior day, `INS-20260729-100047-116b` ("PHASE 2 MERGE, FINAL (v2)...") and `INS-20260729-115036-9a73` ("STAGE 7 DECISION (2026-07-29): Option B chosen — adopt UTM..."), both under `session_id: veridian-consolidated-completion-2026-07-29`. These plausibly are the real origin, but two real gaps remain: (a) the phrasing ("STAGE 7 DECISION... Option B chosen") reads like an AI-authored decision record, not verbatim Owner words — the schema has no field distinguishing "verbatim Owner text" from "AI-authored summary attributed to the owner channel," so `utm_source='owner_chat'` is not reliable proof of literal Owner authorship; (b) getting from the PR to this row required three manual, non-mechanical correlation steps (metadata_json → campaign-slug text match → free-text search) — nothing about the chain is click-through/automatically joinable today.

**Honest verdict: traceability is possible in this case, but only via manual detective work across three tables with no foreign keys between them, and it terminates in a decision-record whose Owner-vs-AI authorship the schema itself cannot distinguish. It is not the "real, followable chain" the Owner is asking for — it is closer to "reconstructible with effort by someone who already knows what to look for."**

## Bottom line

Real and enforced today: the postflight `--audit-cmd` verbatim-copy anti-self-cert rule (Q3, when actually invoked), the task-lifecycle file layout under `ai-os/tasks/{id}/` for anything that reaches `cmd_submit` (Q5, conditional), and the rename-don't-delete convention for superseded docs (Q4, partial/manual).

Aspirational / not enforced today: pre-dispatch reuse checking against capability_registry/wiring_registry (Q1 — the one real tool for this, `plan_generator.py`, is wired to nothing), continuous during-work policy monitoring and CI-equivalent gates on the Owner-side scripts/ai-os trees (Q2 — those trees aren't even under version control), consistent use of the completion gate for recent work (Q3 — 3-day gap in `task_audits`), a documentation-presence gate before `closed` status (Q4), unconditional versioning of gateway.py's own outputs (Q5 — this very audit's Part-1 run proves it), and mechanical (as opposed to manual-detective) traceability (Q6).

Registered via `register-knowledge` and summarized via `log-instruction`, utm_campaign=`owner-engine-e2e-audit-2026-07-30`, so a future AI session can read this instead of re-investigating.
