# VERIDIAN Master Architecture — Plain-Language Summary + Full Technical Plan

**Date:** 2026-07-29
**Status of this document:** This is the authoritative, current record of VERIDIAN's architecture. It replaces all earlier drafts and self-critique passes. Part 1 below is written for a non-technical reader (the Owner). Part 2 is the full technical plan, unedited, for anyone building against it.

---

# PART 1 — Plain-Language Summary (for the Owner)

## The one-paragraph version

VERIDIAN is the AI-powered business software system you're building. Right now it has two "sides": the side that does work *for you* (the Owner) — that part is real, mostly working code — and the side that would let *your paying customers* talk to it directly, which doesn't exist yet, not even a little. The part that *is* built has a safety brake, and that brake has been stuck on for the entire investigation that produced this document — meaning the automatic "get things done" machinery has not actually done anything for hours, and nothing paged you about it. Nothing is catastrophically broken; it's more like a fuse blew three days ago and the breaker box has been sitting there, tripped, silently, ever since. This document explains what's true today, what's still a drawing on paper, and exactly what needs your decision to move forward.

## 1. What is VERIDIAN, really?

Think of VERIDIAN as two things bolted together:

1. **A brain and a pair of hands for you** (called **OWNER_ENGINE** in the technical plan). You type or speak an instruction, and this part of the system is supposed to turn it into real work — writing code, updating a database, generating a report — without you having to do any of the plumbing yourself.
2. **A future "assistant" for your customers** (called **END_USER_ENGINE**). This is meant to be the thing a paying customer talks to when they log into one of your branded products (like PROJEXA) and ask "what's my compliance status?" or "show me this month's numbers." **This does not exist yet.** Zero code has been written for it. It is a plan, not a product.

Both sides are meant to eventually share some of the same underlying machinery — the same database, the same "figure out what work needs doing and go do it" pipeline — but they need to be kept separate in important ways, which is a big part of what this plan is about.

## 2. The "conveyor belt" — how a request turns into finished work

Picture a factory floor. A request comes in one end (say, "add this feature to the compliance tracker"), and if everything's working, a finished, tested, delivered result comes out the other end, with no human needing to physically build it.

Here's the real conveyor belt, in order:

1. **The front door** (`gateway.py`) — reads your raw instruction, figures out roughly what you're asking for, and cleans it up into something the rest of the system can act on. This part works.
2. **The intake queue** (`resource_governor.py`) — takes that cleaned-up request and puts it in line. It checks for duplicates (so you don't accidentally get the same thing built twice) and enforces some basic traffic rules. This part works.
3. **The actual "start the work" trigger** — every 30 seconds, something is supposed to look at the queue and say "okay, next item, go." **This is the weak link, explained in section 3 below.**
4. **The worker** (`dispatch_core.py`) — when triggered, this actually spins up a real, isolated worker (like assigning a task to one specific machine on the factory floor) that does the coding/writing/data work.
5. **The record book** (`superboss-register.sqlite`, a database file) — every step along the way gets logged here, so there's a paper trail of what was asked for, what was done, and when.

There are exactly two known, deliberate shortcuts around this conveyor belt (both documented and intentional, not accidents) — a manual "break glass" bypass for genuine emergencies, and a narrow status-checking script that never spins up new workers so it can't cause the traffic problems the queue exists to prevent. Everything else is supposed to go through the belt in order.

## 3. The alarm clock that's turned off — the current emergency, explained simply

Step 3 above — "something looks at the queue every 30 seconds and says go" — is *supposed* to be handled automatically, like a factory's shift-change bell that rings on a fixed schedule whether or not anyone's watching. In VERIDIAN's case, that automatic scheduler is a system called **cron** (think of it as a bank of alarm clocks, each one set to trigger a different recurring job).

**All twelve of those alarm clocks are currently switched off.** They were turned off three days ago (2026-07-26) after the system ran itself out of memory (like a computer that opened too many programs at once and froze) — a reasonable emergency response at the time. But they were never turned back on.

Right now, the only thing making the conveyor belt move at all is something one of the AI sessions started **by hand** — like someone walking over and holding a switch down themselves, instead of it being on the automatic timer. This hand-started process has no safety net: if it crashes, nothing notices and nothing restarts it. It isn't hooked up to the "restart automatically if it dies" system (called `systemd`, which is the proper, supervised way to run something like this) — it's just running loose in a terminal session called `screen`.

**And right now, even that hand-held switch isn't working**, because of a second, separate safety mechanism:

### The circuit breaker that's stuck

VERIDIAN has a safety feature called **EMERGENCY_STOP** — like a circuit breaker that trips if it senses something dangerous (in this case, the disk being used too heavily — pinned at 100% twice in the last twelve hours). When it trips, it deliberately refuses to start any new work, to protect the server from being overloaded.

**That breaker tripped this morning at 12:21 AM and has not been reset.** Every 30 seconds since then, the system checks in, sees the breaker is tripped, and does nothing — over and over, for hours, with the backlog of pending work just sitting there unprocessed. There is no equivalent of a phone alert or a warning light on a dashboard for this — the only record is a note appended to a text file that nobody is watching in real time. It's the equivalent of a smoke detector that, instead of beeping, quietly writes "smoke detected" in a notebook in a drawer.

**Bottom line: nothing catastrophic is happening (no data is being lost, nothing is being corrupted), but the automatic "get work done" pipeline has been completely idle for hours, and you had no way of knowing that until this document told you.** Fixing this — properly, with real supervision and real alerting — is the very first thing this plan calls for, before anything else gets built.

## 4. The "Google search for VERIDIAN" feature — what it is, and a real security decision inside it

One of VERIDIAN's planned capabilities is letting the AI (and eventually your customers) search across everything the system knows about — code files, database tables, GitHub pull requests, deployed websites — the way you'd Google something, instead of having to know exactly where to look.

**Today, this only searches a small internal notebook** — a database of about 113 catalogued "things" plus some activity logs. It does **not** yet search GitHub, your live website deployments (Vercel), or your actual customer database (Supabase). Calling it "search everything" today would be inaccurate; it's closer to "search a small index card box in the corner of a much bigger library."

### Why this matters for security

Here's the important part, explained with an analogy: imagine two filing cabinets.

- **Filing cabinet A** (your live customer database, called Supabase/Postgres) has a **security guard built directly into the lock**. No matter who tries to open a drawer, or how, the lock itself checks their ID and only lets them see files that belong to them. This is proven and already working — 314 separate places in the code rely on it, and it's been verified to "fail closed," meaning if anything goes wrong, it defaults to *denying* access rather than *allowing* it. This is the gold standard.

- **Filing cabinet B** (the small search notebook mentioned above, called SQLite) has **no built-in guard at all**. If you want security on this cabinet, someone has to remember to write "only show this drawer to the right person" into every single piece of code that ever opens it — and if even one programmer forgets that check in one place, that's a real hole, silently.

An earlier draft of this plan proposed just adding a "who's allowed to see this" label to filing cabinet B and calling it good enough. **This plan corrects that — a label alone isn't a real guard, it's a sticky note, and stickies fall off.** Instead, this plan lays out two real options:

- **Option A (recommended): move the parts of the search notebook that customers would ever see into filing cabinet A** — the one with the guard already built in and already proven. Keep only your own private operational notes in the un-guarded cabinet, since customers should never see those anyway.
- **Option B (fallback): keep everything in the un-guarded cabinet, but force every single lookup to go through one single checkpoint function** that refuses to show anything unless it's explicitly labeled as safe to show — defaulting to "hide it" rather than "show it" — and have an automatic test that runs on every code change to make sure that checkpoint can never accidentally be skipped.

This plan recommends Option A. Either way, this is a real decision that needs to be made deliberately, not an afterthought — it's listed in the Owner decision list below.

## 5. Keeping your business logic away from customers — the "vault key" problem

Today, when the Owner's AI dispatches work, it does so with fairly broad permissions — including the ability to write code into your real GitHub repositories and push changes to your live websites (Vercel). That's appropriate for you, the Owner, giving instructions.

**It would not be appropriate for a random paying customer to have that same power by accident.** This plan requires that whenever END_USER_ENGINE (the not-yet-built customer-facing assistant) needs to hand off a task to the same conveyor-belt machinery, it must do so using a **restricted worker identity that, by default, holds no key to your code repositories or your live deployment systems at all.** Getting that extra key would require a separate, explicit, Owner-approved step — never automatic.

**This restriction mechanism does not exist yet.** Until it's built, the plan is explicit: END_USER_ENGINE is not allowed to touch the code-writing/deployment machinery at all, full stop, no exceptions. This is treated as a hard rule, not a nice-to-have.

## 6. Why customer chat can't just reuse the same conveyor belt

The conveyor belt described in section 2 was built for *project-sized* work — things that take minutes, like writing and testing a piece of code. It was **not** designed for a customer typing "what's my compliance status?" and expecting an answer in a second or two.

This plan fixes that by adding a **receptionist** in front of everything (part of END_USER_ENGINE, not yet built): every message from a customer first gets triaged.

- **If it's a simple lookup** ("what's my status," "show me this report") — the receptionist answers it immediately using the search/database layer directly, without ever touching the conveyor belt. No worker gets spun up, no 30-second delay, and — importantly — it's completely unaffected by the conveyor belt being down (like it is right now).
- **If it's genuinely a task** (something requiring real work to be done, like generating a brand-new custom report or making a data change) — *then* it gets routed into the shared conveyor belt, under the same restrictions as section 5, and subject to the same current outage risk as everything else on that belt.

Most customer interactions should be simple lookups, so this design change is what keeps the (currently fragile) conveyor belt out of the way of most day-to-day customer use.

## 7. What's real today vs. what's still just a plan

| Piece | Status |
|---|---|
| The Owner's own request-handling front door | **Real, working** |
| The intake queue / duplicate-check | **Real, working** |
| The automatic 30-second trigger that starts work | **Real code exists, but currently not running on a supervised schedule — running by hand, unsupervised, and currently blocked by the tripped safety breaker** |
| The actual worker/task-runner | **Real, working when triggered** |
| The activity record book (database) | **Real, working** |
| The "search everything" feature | **Small, partial version real; full version (GitHub/Vercel/Supabase/code search) not built** |
| Multi-tenant customer data separation (keeping different customers' data apart) | **Real, working, and independently verified as the one part of this whole system that is exactly as solid as originally claimed** |
| The customer-facing assistant (END_USER_ENGINE) | **Does not exist. Zero code.** |
| The "restricted worker identity" that would keep customers away from your code/deployment systems | **Does not exist yet — must be built before customers can be let in at all** |
| Automatic alerting when something breaks (like the current stuck breaker) | **Does not exist — currently just a text file nobody watches** |

## 8. The plan going forward, in plain terms

**Step 0 — Fix the alarm system (first, before anything else, and doesn't require any new design work — just fixing operations):**
- Decide whether to clear the currently-tripped safety breaker (your call, not this document's).
- Put the "start work every 30 seconds" trigger onto a properly supervised system that restarts itself if it crashes, instead of running loose by hand.
- Replace the "silent note in a text file" alerting with something that actually reaches you — a phone push notification, an email, or similar.
- Clean up a small piece of leftover dead configuration that points at a file that no longer exists.
- Move test/experimental workloads off the same lane as real production work, so a stress test doesn't trip the same breaker again.
- Double-check the "disk usage at 100%" reading that trips the breaker against an independent measurement — right now the system is only trusting its own self-report, which has a history of false alarms.

**Two other initiatives are already running independently and this plan deliberately does not duplicate them** — one is cleaning up redundant/duplicate automation scripts, the other is building the real Owner-side/customer-side split. This plan feeds its own requirements (the receptionist idea in section 6, the restricted-worker-identity rule in section 5) into that second initiative rather than competing with it.

**Step 3 — Build the real search layer:** gather all the scattered inventory files into one place, make the Option A vs. Option B security decision from section 4 for real, and add the missing GitHub/Vercel/Supabase search coverage.

**Step 4 — Build the actual customer-facing front door (END_USER_ENGINE):** the receptionist/triage logic from section 6, the restricted-worker-identity fence from section 5 (a hard requirement before this step can finish), and login/signup handling (from the other initiative mentioned above).

**Step 5 — Prove it can handle real load before letting any real customers in:** today the system has only ever handled traffic from you, the Owner. Nobody has tested what happens with dozens or hundreds of simultaneous customer requests. This step is explicitly a gate — **no real customers get access to END_USER_ENGINE until this testing is done and passes.**

**Step 6 — A calendar check-in on 2026-08-05:** there's a temporary rule limiting which AI service VERIDIAN uses, set to expire on that date. On that date, someone needs to explicitly decide whether to extend it or switch to the originally planned alternative providers.

## 9. Decisions only you can make

This document deliberately stops short of making these calls for you:

1. **Should the tripped safety breaker be cleared now, or left alone until the underlying fix is done?**
2. **Supervised-restart-service vs. restoring the old alarm-clock schedule** — for making the 30-second trigger reliable again. Either works; pick one.
3. **Option A (move search data into the guarded database) vs. Option B (keep it where it is, add a manual checkpoint)** — a real tradeoff between how much work it takes to build vs. how strong the security guarantee is.
4. **What should replace the silent text-file alert** — push notification to your phone? Email? Something else?
5. **Is the 2026-08-05 AI-provider deadline still real, and what should happen automatically if it arrives and the customer-facing side still isn't built?**
6. **What's an acceptable spending limit for AI usage once real customers start using the system?** There's no real usage data yet to size this number against, so this plan deliberately did not invent one — it needs your judgment once there's real traffic to look at.

## 10. What honestly can't be known yet

This plan does not pretend to have already-tested answers for things that require real customer traffic to observe: whether the conveyor belt holds up under genuinely heavy simultaneous use, what the right per-customer usage limits should be, and whether the "100% disk usage" alarm reading can actually be trusted. Those require running the real system under real conditions that don't exist yet — no customers are using it today, so there's nothing to measure yet. Marking these as open and unresolved, instead of guessing, is the honest and correct state of this plan.

---

# PART 2 — Full Technical Plan (Final, Authoritative)

# VERIDIAN Master Architecture Plan — FINAL (2026-07-29)

**This document supersedes `fullArch` and all three self-critique passes as the authoritative reference.** Those four documents remain the evidence trail (cited throughout) but are not to be read as current — `fullArch` in particular contains claims (§1 dispatch diagram, §8 "real, live" table) that this document corrects. Anyone building against this plan should build against **this** document, not `fullArch`.

**Live status check performed at the start of this task (2026-07-29, immediately before writing this document), re-confirming pass 3's finding still holds at time of writing:**
```
EMERGENCY_STOP sentinel: still present, unchanged since 2026-07-29T00:21:33Z (file mtime: Jul 29 00:21)
screen session resource_governor_tick_loop: alive, Detached, running since 07/28 19:46
tick log: still logging "emergency_stopped" every 30s, no change
umr_tasks backlog: completed=12, failed=18, killed=12, queued=10, rejected_duplicate=3, running=7 — byte-identical to pass 2 and pass 3's snapshots hours earlier
```
**The shared dispatch spine has now been continuously halted for the entire duration of this multi-hour investigation, with zero automated alerting, and remains halted right now.** This is not a historical finding about an incident that happened; it is the present operating state. Everything below is written with that fact as a load-bearing constraint, not a footnote — Phase 0 exists because of it.

---

## 1. The one consolidated VERIDIAN system — real named subsystems, corrected

Same component set as `fullArch` §0, with every factual correction from the three critique passes folded in directly (no separate errata list — this table is now the source of truth).

| Component | Real, current state (2026-07-29) |
|---|---|
| **Owner** | raajat.agarwal@gmail.com, sole principal of OWNER_ENGINE. AI-work channel through 2026-08-05: Claude Code CLI direct SSH only (Z.ai SAP-queue exempt) — **time-boxed, re-check required at expiry, see Phase 6**. |
| **Server (VERIDIAN-DEV)** | 167.233.220.35, 8-core. `/opt/veridian/scripts` and `/opt/veridian/ai-os` are not git repos (rename-not-delete). |
| **Automation trigger layer** | **All 12 crontab entries commented out since the 2026-07-26 OOM incident** (`#STOPPED-ALL-CRON-2026-07-26#`). One paused entry (`queue-dispatcher.py`) points at a file that no longer exists on disk — dead pointer, superseded by `dispatch-tick.py`, never cleaned up. `dispatch-tick.py` (the intended consolidated replacement for `supervisor-sweep.sh` + `queue-dispatcher.py` + `module-queue-dispatcher.py`) was **never wired to cron even before the OOM pause** — its own header says so. The thing actually driving dispatch today is a **hand-started `screen -dmS resource_governor_tick_loop`** session (PID 1424771, started 2026-07-28 19:46, no systemd unit, no supervisor, no restart-on-crash/reboot) running a 30-second `--tick`/`--reconcile-stale` loop. |
| **Dispatch spine (code)** | Real, exists: `gateway.py` → `resource_governor.py` (submit/tick) → `dispatch_core.py` → `superboss-register.sqlite`. **Two confirmed, real exceptions to "one path":** (1) `task-gateway.py cmd_start` is deprecated into a flag-gated break-glass bypass of `resource_governor.py`'s concurrency cap, dedup, and EMERGENCY_STOP — the live route no longer calls it, `gateway.py`'s `dispatch_to_task_lifecycle()` calls `resource_governor.py --submit` directly; (2) `status-remediation-tick.py` is a justified, documented carve-out (no worker spawn, so no concurrency risk). |
| **Dispatch spine (operation)** | **Currently halted.** EMERGENCY_STOP sentinel present since 00:21:33Z today, disk_io pinned at 100.0 both times it tripped in the last ~12h (2026-07-28T17:58 and 2026-07-29T00:21), the only alerting artifact (`ATTENTION.md`) is a markdown append with no page/email/Slack, and the health-check cron jobs that would have caught this are among the ones paused since 07-26. |
| **GitHub** | Real repos at `/opt/veridian/repos/{compliance-tracker, projexa, compliance-tracker-projexa-records-wt}` + active PR worktrees. `gh` CLI is a separate ad hoc search path, not indexed into `system_index`. |
| **Vercel** | Deployment targets only (veridian-compliance-ai, projexa, veda-advisors). No live query integration into any index. |
| **Supabase** | 444-table live Postgres. `withTenantContext`/RLS confirmed real and fail-closed (314 call sites, 1085 `orgId` references, verified by direct read of `tenant-scoped.ts`). No live scanner into `system_index`. |
| **Catalogs** | **At least six** files, not two: root `FUNCTION_CATALOG.json` (5019 functions)/`DATABASE_CATALOG.json` (444 tables), plus per-project copies under `ai-os/catalogs/{veridian-ui-kit,projexa,veda-advisors}/`. Freshness has no owner — the cron jobs that would regenerate them are paused (same OOM incident). Root-file counts are not the full catalog surface. |
| **`system_index` registry** | Real, confirmed at the correct path `/opt/veridian/ai-os/memory/superboss-register.sqlite` (a *wrong-but-plausible* path silently returns an empty, valid-looking result — see §5 closure item on this). Row counts reproduced directly this session: `system_index`=113, `instructions`=595, `work_items`=603, `actions`=8416, `log_index`=10938. `sqlite3` CLI is not installed on the box; counts were pulled via Python's `sqlite3` module — note the method for reproducibility. Zero rows from either catalog family are wired in yet. |
| **Brands** (PROJEXA-AI.COM, veda-advisors, etc.) | Thin clients via `callVeridian()` bridge + org-linkage — architecture confirmed, not re-audited this session. |
| **Multi-tenant orgs** | Real, live, fail-closed RLS via `app_runtime` role (no bypass). This is the one part of the whole design that checks out exactly as originally stated across all three critique passes. |
| **End users** | No engine exists. `find /opt/veridian -iname '*end_user_engine*'` → zero results, reconfirmed. |
| **OWNER_ENGINE** | Real, live, but its EMERGENCY_STOP-gated dispatch tail is currently non-operational (see above). |
| **END_USER_ENGINE** | **[DESIGNED, NOT BUILT]** — zero files. |

---

## 2. The Google-Search-like capability — real design, corrected for the adversarial finding on datastore choice

### 2.1 What exists today
A curated, partial, SQLite FTS5 registry (`system_index` + 4 related tables) — not a comprehensive index of GitHub/Vercel/Supabase/browser state. This was the honest starting point established this session and nothing found since changes that.

### 2.2 The design change this document makes versus `fullArch` §4

`fullArch` proposed adding a `visibility` column to `system_index` (SQLite) and treating it as the search-layer analogue of Supabase's RLS. **The adversarial review is correct that this is not a "not yet built" feature gap — it is a datastore-choice problem.** SQLite has no session-GUC/row-security engine equivalent to Postgres RLS. An application-layer `WHERE visibility = ...` clause in SQLite can be forgotten in exactly the way the Supabase design explicitly credits RLS for making impossible. Pass 2's own B6 (querying the wrong-but-plausible DB path and silently getting an empty, valid-looking result instead of an error) is a live demonstration of the same class of silent-failure risk in this exact registry.

**Resolution — pick one of two real paths, not a cosmetic column:**

- **Path A (recommended): move the multi-tenant-visible slice of `system_index` into Supabase/Postgres**, behind the same `withTenantContext`/RLS mechanism already proven fail-closed for 314+ call sites. The Owner-only slice (instructions/work_items/actions/log_index — Owner's own operational history) can stay in SQLite since it is never end-user-visible by design. Only the portion end users can query (the registry/search surface) needs RLS-grade enforcement, and Postgres already has it.
- **Path B (if Path A is rejected for operational reasons — e.g., not wanting to add Supabase write load to the registry):** keep `system_index` in SQLite, but enforce visibility with a **fail-closed wrapper function**, not a raw column check: every read goes through one function that (a) requires an explicit, non-null `visibility` tag on the row or the row is excluded by default (deny-by-default, not allow-by-default), and (b) is covered by a mechanical test that asserts "a row with a missing/malformed visibility tag never appears in a scoped query result" — run as a CI gate, not a design intention. This is weaker than RLS (still application-layer) but at least matches the "fail closed" bar the Supabase design sets, instead of falling below it.

**This document recommends Path A** and treats Path B as the fallback if Path A proves infeasible during Phase 3 build-out. Either way, the choice must be made explicitly and recorded — `fullArch`'s implicit assumption that a column addition alone gets SQLite to RLS-equivalent behavior is retracted.

### 2.3 Cost tiering (unchanged from `fullArch`, still sound)
SQL/Postgres full-text search (near-zero cost, default) → embedding similarity (`capability-registry-service.ts`, reused not rebuilt) only on ambiguous multi-match → single AI adjudication (Claude Code CLI only, per the 2026-08-05-bounded constraint) only if still ambiguous → full reasoning session only for genuine non-existence questions.

### 2.4 What populates it, corrected for A3/A4
Bulk-load **all six-plus** catalog files with an explicit brand/org tag per source (root files treated as a to-be-verified superset, not assumed authoritative over per-project copies until checked), then add scanners for `github_pr`/`github_issue`, `vercel_deployment`, `supabase_schema` (via the platform's own MCP), and `process_state` (crontab/systemd/screen-session diff — see Phase 0 for why this scanner must not be built before the underlying automation layer is stabilized, or it will either silently miss the 12 paused jobs, parsed as comments, or falsely resurrect them). Catalog freshness is explicitly a **blocked dependency** on Phase 0's automation-layer fix, not a one-time ETL step — stated honestly rather than assumed solved by a bulk-load.

---

## 3. OWNER_ENGINE / END_USER_ENGINE — real relationship and real data flows, corrected

### 3.1 Corrected dispatch diagram (replaces `fullArch` §1, which cited a deprecated path)

```
raw input
   │
   ▼
[gateway.py --mode owner-dispatch]   (OWNER_ENGINE front door — real, live)
   classify → VD- chat id → noise-strip → pruned prompt
   │
   ▼
[resource_governor.py --submit]      (queue enqueue only — confirmed: submit() never calls dispatch)
   per-identity dedup of SEQUENTIAL submissions (confirmed present)
   NO per-tenant/aggregate ceiling logic anywhere in this file (confirmed by grep — see §5 closure)
   │
   ▼
[resource_governor.py --tick]        (actual spawn trigger)
   ── currently invoked ONLY by a hand-started, unsupervised `screen` loop ──
   ── currently returns "emergency_stopped" on every tick (live right now) ──
   │
   ▼
[dispatch_core.py]  acquire_dispatch_lock() + has_free_slot() + transient systemd unit spawn
   (unit names confirmed real via ATTENTION.md SIGTERM log: veridian-worker@<task-id>.service —
    this resolves pass 1's "zero systemctl matches" as a timing artifact, not a missing mechanism)
   │
   ▼
[superboss-register.sqlite]  system_index / instructions / work_items / actions / log_index

KNOWN, DOCUMENTED EXCEPTIONS to this path (must be positively enumerated, not just absent from grep):
  1. task-gateway.py cmd_start — deprecated, flag-gated break-glass bypass (--i-understand-this-bypasses-resource-governor)
  2. status-remediation-tick.py — justified carve-out, mechanical gh-only actions, no worker spawn
```

### 3.2 The workload-shape correction (closes adversarial finding #2)

`fullArch` §5 routed **all** end-user chat traffic through this exact spine — the same per-task, systemd-unit-per-item, 30-second-tick-poll pipeline built for spawning coding/PR work. That pipeline is architecturally wrong for synchronous customer Q&A: a customer asking "what's my compliance status" should not wait on a worker-unit spawn cycle designed for a multi-minute PR job, and should not consume a dispatch slot that competes with real Owner work.

**Corrected design: END_USER_ENGINE's front door classifies every inbound message before it touches the dispatch spine at all:**

```
End-user message → END_USER_ENGINE front door
   │
   ├─ Classify: answerable via search/registry (§2) or a deterministic engine
   │  call (VCEL engines, direct Supabase read via withTenantContext)?
   │      YES → synchronous query path. No worker spawn, no dispatch-spine
   │            involvement, no EMERGENCY_STOP exposure, no 30s tick latency.
   │            This is the majority-case path for real customer support/status
   │            questions and should be the default assumption, not the exception.
   │
   └─ Classify: genuinely requires dispatched work (code change, PR, multi-step
      agentic task)?
          YES → routes into the shared dispatch spine (§3.1), scoped by
                visibility=tenant:<org_id>, subject to the same governance
                and the same current outage risk as Owner traffic.
```

This does two things `fullArch` didn't: it keeps the (currently fragile, currently down) dispatch spine off the hot path for most end-user interactions, and it gives a concrete, checkable meaning to "thin front door" — END_USER_ENGINE's classifier is the new component, not a second dispatch mechanism.

### 3.3 The repo-write barrier (closes adversarial finding #1)

`fullArch` §6 asserted "end users never touch GitHub/Vercel directly" with no mechanism. **Corrected requirement:** any task routed into the dispatch-spine path (§3.2) on behalf of an end user must run under a **capability-scoped worker identity that holds no GitHub write credential and no Vercel deploy credential by default.** Repo-write/deploy actions require a distinct, explicit elevation step gated by Owner approval (or a pre-approved, narrowly-scoped automation rule set up by the Owner in advance) — not the ambient credentials the Owner's own AI Dev Team dispatch (`roster.ts`, `dispatch-repo.ts`) currently runs with. **This credential-scoping mechanism does not exist yet and must be built as part of Phase 4** (§4 below); until it exists, END_USER_ENGINE must not be allowed to reach `dispatch-repo.ts` at all, full stop — this is a hard precondition, not a nice-to-have.

Note on `roster.ts`/`dispatch-repo.ts` "confirmed real/live" citation in `fullArch` §5: **this was never independently re-opened during this session** (pass 2 flagged it, pass 3 didn't re-check it either). It is carried forward as a prior-session claim, not a fresh read — flagged honestly rather than re-asserted as newly confirmed.

### 3.4 Shared vs isolated table (corrected from `fullArch` §6)

| Layer | Owner flow | End-user flow | Shared or isolated |
|---|---|---|---|
| Entry channel | SSH / Claude Code CLI | Web/PWA, external API-on-behalf, external chat-on-behalf | Isolated |
| Front-door engine | `gateway.py` (real) | END_USER_ENGINE (not built) — now includes a query/task classifier (§3.2) | Isolated control planes |
| **Query path (new)** | N/A — Owner uses direct search/registry calls | Synchronous search/registry/deterministic-engine answers, no worker spawn | **Shared registry (§2), no dispatch-spine involvement** |
| **Task-dispatch path** | Direct | Only for classified "genuine work," under repo-write barrier (§3.3) | **Shared spine — currently down, see Phase 0** |
| Resource governance | `resource_governor.py`, no per-tenant ceiling (confirmed absent) | Same, unmitigated | Shared, **unresolved gap**, see §5 |
| Persistence | `superboss-register.sqlite` | Same | Shared |
| Search/registry | `system_index` | Same table (Path A: Postgres/RLS slice) or fail-closed wrapper (Path B) | Shared data, RLS- or wrapper-scoped |
| Application data | Supabase, unscoped | Supabase via `withTenantContext`, RLS-enforced | Shared DB, RLS-isolated |
| Repo-write / deploy | Direct, ambient credentials | **Blocked by default**, explicit elevation only (§3.3) | Isolated by credential scope |
| AI provider | Owner-provided, Claude Code CLI only through 2026-08-05 | Same today; org-BYOM future option | Shared today, time-boxed (Phase 6) |

---

## 4. Staged implementation order

This order is explicit about which stages are **this document's own new work** versus **stages this document defers to already-running independent workflows**, per the standing instruction not to duplicate `UNCOMPLICATE_UNDUPLICATE_TASK` or `PARALLEL_COMPLETION_OF_TASKS`.

**Stage 2-6 (OWNER_ENGINE consolidation)** — complete, per `wf_546e4f25-636`. Real dispatch routes through `resource_governor.py`, RCE found+fixed, chat/instruction/task cross-referencing works. Disclosed unfixed gaps carried forward: same-text resubmission dedup, `document_engine.py` corruption bug, FTS false-duplicate bug, EMERGENCY_STOP false-trip (now observed live and worse than "disclosed" — see Phase 0), pre-migration heartbeat-NULL rows.

**Phase 0 — Operational stabilization (blocking, before anything else in this plan; Owner-actionable now, does not require design work).** This phase exists solely because of this session's live finding that the spine is down, not because of any prior plan step:
1. Clear or diagnose the current EMERGENCY_STOP sentinel (Owner decision — this document does not clear it; read-only investigation only, left exactly as found).
2. Convert `resource_governor_tick_loop.sh` from an unsupervised `screen` session into a supervised systemd service (or restore the crontab entries with the OOM root cause actually fixed) — either is acceptable, "some form of supervised, restart-on-crash trigger" is the requirement, not a specific mechanism.
3. Replace `ATTENTION.md`'s dead-letter markdown append with an active page (e.g. a push notification to the Owner) on every EMERGENCY_STOP trip and every shed-load SIGTERM burst.
4. Clean the stale `queue-dispatcher.py` crontab pointer (dead file reference) — trivial but real registry debt that will otherwise corrupt the Phase 3 `process_state` scanner.
5. Isolate test/scenario/stress workloads (confirmed running through the production dispatch tier at production priority — the named `vd-stress-2`/`scenario-test-15-probe-b` units immediately preceding the second EMERGENCY_STOP trip) onto a separate queue, priority tier, or box, so that scale-verification work (Phase 5) doesn't reproduce the exact outage this phase is fixing.
6. Cross-validate the `disk_io=100.0` metric that triggered both trips against an independent source (`iostat`/`iotop`) before trusting it as ground truth for any future tuning — `resource_governor.py`'s self-reported metric has an already-disclosed false-trip history and was never independently corroborated this session (adversarial finding #4). Until cross-validated, treat the 100.0 reading as "the system's own claim," not confirmed fact.

**`UNCOMPLICATE_UNDUPLICATE_TASK`** (running independently) — engine sprawl, cron/systemd consolidation, metadata unification, the 7 architecture principles' mechanical-check tooling. **This document defers to its outcome** for exactly how the automation-trigger layer gets consolidated; Phase 0 above is a minimal stopgap, not a substitute for that workflow's fuller fix.

**`TWO_ENGINE_TASK`** (running independently) — the real OWNER_ENGINE/END_USER_ENGINE split. **This document defers to its outcome** for END_USER_ENGINE's authentication/onboarding design specifics, feeding it §3's corrected data-flow diagram, the query/task classifier requirement (§3.2), and the repo-write barrier requirement (§3.3) as inputs, not as a competing design.

**Phase 3 (this document's own scope) — Search/registry layer.** Bulk-load all six-plus catalogs with brand/org tagging (§2.4), make and record the Path A vs Path B decision (§2.2), build the GitHub/Vercel/Supabase/process-state scanners (process-state scanner only after Phase 0 lands, per §2.4's caution), implement the cost-tiered query path.

**Phase 4 (this document's own scope) — END_USER_ENGINE front door build**, informed by `TWO_ENGINE_TASK`'s output: auth/onboarding (per whatever `TWO_ENGINE_TASK` lands on), the three input channels, the query/task classifier (§3.2), the capability-scoped repo-write barrier (§3.3, hard precondition before any dispatch-spine exposure), 24h auto-close reconciled with freeze-state (§5 closure item), cost ceiling / AI-necessity triage (§5 closure item).

**Phase 5 — Scale verification (principle 6).** Load-test the dispatch spine at meaningfully higher concurrency than today's Owner-only traffic, using the isolated test tier from Phase 0 step 5, with real per-tenant/aggregate ceiling logic added to `resource_governor.py` (currently absent, confirmed by grep) and real capacity math reconciling the 8-core box against "hundreds of concurrent queries" — either a horizontal-scaling plan or an explicit backpressure/queueing model, not "freeze everything at 99%" as the only control. **END_USER_ENGINE does not onboard real end users until this phase passes.**

**Phase 6 — AI-provider transition.** Explicit re-check at 2026-08-05: revert to OpenRouter/Groq/Cerebras per the existing AI Router work, or Owner extends the CLI-only window. This is a calendar-triggered decision point, not a one-time design assumption.

---

## 5. Itemized closure of every gap raised — genuinely closed, or honestly flagged open

### From Self-Critique Pass 1

| # | Gap | Disposition |
|---|---|---|
| A1 | Cron presented as live; actually all paused since 07-26 | **CLOSED (in this document's facts)**: §1 table now states the true state. Operationally still open until Phase 0/`UNCOMPLICATE_UNDUPLICATE_TASK` lands. |
| A2 | `systemctl` showed zero veridian units | **CLOSED**: pass 3 confirmed via ATTENTION.md SIGTERM log that transient `veridian-worker@<task-id>.service` units are real; zero-match was a timing artifact of short-lived units, not a missing mechanism. |
| A3 | Catalog count undercounted (2 vs 6+) | **CLOSED (in this document's facts)**: §1 and §2.4 now state 6+ files and require an explicit merge/tag decision in Phase 3 rather than assuming "bulk-load the two." |
| A4 | Catalog freshness has no owner, source cron paused | **Explicitly flagged OPEN**: stated as a blocked dependency on Phase 0/automation-layer fix in §2.4, not silently assumed solved. |
| A5 | Docstring-attribution claim was a paraphrase-of-a-paraphrase | **CLOSED**: pass 2 confirmed the admission exists only in `resource_governor.py`'s docstring describing `dispatch_core.py` externally, not in `dispatch_core.py` itself (244 lines grepped, zero matches). §3.1 no longer repeats the misattribution. |
| A6 | Row counts not reproducible with standard tooling (`sqlite3` not installed) | **Partially closed**: pass 2 reproduced the counts via the correct path using Python's `sqlite3` module and they matched. **Flagged OPEN**: `sqlite3` CLI still isn't installed on the box, so the next reviewer needs to know the method, not just trust the numbers — stated explicitly in §1. |
| A7 | `content_hash` exists for a different purpose than idempotency | **CLOSED (documented, not built)**: §1/design note carried forward — a primitive exists in the codebase for change-detection, not dedup; principle 4 (dual idempotency keys) remains genuinely unbuilt and must not be assumed solved because a same-named field exists. Still an open build item, honestly labeled as such. |
| B1 | Grep-based "one spine" check is defeatable | **Partially closed, partially OPEN**: §3.1 now requires a **positive enumerated allowlist** of exceptions (the two known ones) rather than a pure absence-of-new-strings grep. **Genuinely cannot be fully closed on paper**: no runtime enforcement (OS-level single entry point, exec-restriction) exists or is proposed here as mandatory — that would be a significant architecture change beyond this document's scope, and is flagged as a real residual risk rather than papered over. |
| B2 | EMERGENCY_STOP known bug → shared blast radius once end users land | **CLOSED as a sequencing gate**: Phase 0 is now a hard blocking precondition before Phase 4/5, specifically because of this bug, not folded into a generic "scale-verify" footnote. |
| B3 | 24h auto-close vs freeze-state not reconciled | **Flagged OPEN, with a concrete requirement**: Phase 4 must make the 24h timer freeze-aware (pause the countdown, or at minimum notify the end user, during a known system-wide freeze) — not solved here because it hasn't been designed yet, only specified as a Phase 4 acceptance criterion. |
| B4 | `visibility` filter is application-layer only, inconsistent with the document's own RLS security bar | **CLOSED via design change**: §2.2 replaces the plain-column proposal with Path A (move to Postgres/RLS) or Path B (fail-closed wrapper + CI-enforced test), directly addressing the inconsistency instead of restating it as a future feature. |
| B5 | Capacity math never done; 8-core vs hundreds of concurrent queries | **Flagged OPEN, explicitly**: Phase 5 requires real capacity math and either horizontal scaling or backpressure — **this document does not claim to have solved it**, because it requires load data that doesn't exist yet. Honestly stated as unresolved, not assumed away. |
| B6 | Owner-side single-layer defense-in-depth | **Flagged OPEN**: noted in §1/§3 that the Owner path has only `run_owner_engine_gate()` as a static, application-layer control, with no second independent layer, given a real RCE was already found once in this spine. No second layer is proposed here — genuinely unresolved, stated as such rather than dismissed via "Owner is unscoped by design." |
| B7 | 2026-08-05 AI-provider constraint treated as permanent | **CLOSED as a process**: Phase 6 makes this an explicit calendar-triggered decision point with two named outcomes (revert to OpenRouter, or Owner extends), rather than a silent fixed assumption. |
| B8 | Principle 5 (review gate) has no mechanism, threshold, or owner | **Flagged OPEN**: not resolved in this document — doing so requires an actual CI/process design exercise. Stated honestly as unbuilt rather than restated as "will be reviewed." |

### From Self-Critique Pass 2

| # | Gap | Disposition |
|---|---|---|
| A1-upgrade | Dead crontab pointer to a deleted file | **CLOSED as a task**: Phase 0 step 4 explicitly requires cleaning this before the Phase 3 process-state scanner is built. |
| A5-upgrade | Confirmed misattribution (not just unconfirmed) | **CLOSED**: reflected in §3.1's corrected diagram and wording. |
| A6-reproduced | Row counts confirmed correct via right path | **CLOSED**: incorporated into §1 with the caveat about `sqlite3` CLI absence preserved. |
| B1 | Entire spine actually run by unsupervised `screen` loop | **CLOSED as the central finding driving Phase 0**: this is the single biggest correction this document makes to `fullArch`'s "real, live, complete" framing — now stated at the top of the document and as Phase 0's justification, not buried. |
| B2 | `task-gateway.py cmd_start` is a deprecated bypass; real route is different | **CLOSED**: §3.1's diagram now reflects the real route and explicitly enumerates `cmd_start` as a known, flag-gated exception rather than presenting it as the live path. |
| B3 | `status-remediation-tick.py` is a second, justified carve-out | **CLOSED**: enumerated alongside `cmd_start` in §3.1 as one of exactly two known exceptions, both positively documented. |
| B4 | `dispatch-tick.py` never wired to cron even pre-OOM; a second dormant piece | **Flagged OPEN, explicitly**: §1 states this; Phase 0/`UNCOMPLICATE_UNDUPLICATE_TASK` must decide whether `dispatch-tick.py`'s three consolidated sub-behaviors (supervisor-sweep, gap-queue, module-queue dispatch) are running via any path at all — **this document does not know the answer and does not guess it**. |
| B5 | No per-tenant/aggregate ceiling logic anywhere in `resource_governor.py` (confirmed by grep, not inferred) | **Flagged OPEN, upgraded to a hard Phase 5 gate**: §4 makes real per-tenant/aggregate ceilings a named Phase 5 deliverable, not a footnote. |
| B6 | Wrong-but-plausible DB path silently returns empty, valid-looking result | **CLOSED via design principle**: cited directly in §2.2 as the concrete justification for requiring fail-closed (deny-by-default) behavior in whichever path (A or B) is chosen for the visibility filter — this failure mode is exactly what B4/adversarial-#3's fix must prevent. |
| B7 | Orphaned concurrent processes from other uncoordinated sessions on the same box | **Flagged OPEN, situational**: noted as a live instance of the known coordination-gap risk class (already tracked in `MEMORY_OWNER_AI.md`); no new mechanism proposed here beyond what that existing lessons file already covers — not this document's scope to re-solve. |

### From Self-Critique Pass 3

| # | Gap | Disposition |
|---|---|---|
| Headline finding | Spine is EMERGENCY_STOPPED right now, 5+ hrs at time of writing, no paging | **CLOSED as the document's framing**: stated in the opening section, re-confirmed live at the start of this task (still active), and is Phase 0's entire reason for existing — not downgraded to a footnote anywhere in this document. |
| disk_io=100.0 reproducible pattern, test workloads at production priority | **CLOSED as a Phase 0 task**: step 5 (isolate test/scenario load) directly targets this. |
| systemd transient units confirmed real | **CLOSED**: folded into A2's resolution above. |
| "confirmed to exist in code" vs "confirmed operating" distinction | **CLOSED as a documentation discipline**: this entire document distinguishes the two explicitly (e.g., §1's automation-trigger-layer row, §3.1's diagram annotations) rather than using "real, live" as a single undifferentiated status. |
| 24h auto-close now concretely dangerous, not hypothetical | **Folded into B3 above** — same disposition, now with the added urgency that it already would have caused silent harm had END_USER_ENGINE existed during the observed outage window. |

### From the independent adversarial review

| # | Gap | Disposition |
|---|---|---|
| 1 | No enforced barrier stops end-user tasks reaching GitHub/Vercel repo-write | **CLOSED via design change**: §3.3 makes a capability-scoped, credential-restricted worker identity a hard precondition for Phase 4, with END_USER_ENGINE explicitly forbidden from reaching `dispatch-repo.ts` until it exists. **Not yet built** — the requirement is closed, the implementation is a named Phase 4 deliverable. |
| 2 | Chat traffic architecturally mismatched to the per-task dispatch pipeline | **CLOSED via design change**: §3.2 introduces the query/task classifier and synchronous query path as the actual fix, not a restatement of the problem. |
| 3 | SQLite `system_index` can't get real RLS-equivalent filtering (datastore problem) | **CLOSED via design change**: §2.2's Path A/Path B replaces the plain-column proposal with either a real migration to Postgres/RLS or an explicitly fail-closed wrapper with a CI-enforced test — acknowledges this is a datastore decision, not a feature checkbox. |
| 4 | `disk_io=100.0` never independently corroborated; trusting the tool's own metric | **Flagged OPEN with a concrete task**: Phase 0 step 6 requires `iostat`/`iotop` cross-validation before the metric is trusted for tuning decisions — **not corroborated in this document either**, since doing so requires live access at the moment of a trip, which this read-only investigation did not attempt. Stated honestly as unverified, not asserted as fixed. |
| 5 | `fullArch`'s own text was never corrected; stale claims survive alongside critiques | **CLOSED**: this document is explicitly declared as the superseding, authoritative version in its opening line — `fullArch` is now evidence trail only. |
| 6 | No plain-language Owner decision list across ~15,000 words | **CLOSED**: §6 below. |
| 7 | No cost ceiling / AI-necessity triage for end-user volume | **Flagged OPEN with a concrete requirement**: named as a Phase 4 acceptance criterion in §4 — the query/task classifier (§3.2) is the mechanism that would host it (route to free/cheap deterministic paths first), but the actual cost ceiling numbers are not set in this document because no end-user volume data exists yet to size them against. Honestly incomplete, not fabricated. |
| 8 | "AWS SaaS ref pattern" citation never re-verified this session | **Flagged OPEN**: §3.3/§1 note explicitly that this citation is carried forward from a prior session and was not reopened by any of the three critique passes or this final pass — stated as unverified rather than re-asserted as confirmed. |

---

## 6. Plain-language summary and Owner decision list

**What's actually true right now, in one paragraph:** VERIDIAN's Owner-side automation (OWNER_ENGINE) is real code that mostly works, but its automatic dispatch is currently switched off — not broken, off, by its own safety mechanism, because of a resource spike three days ago that it hasn't recovered from, and nothing has told you that in five-plus hours. The "search everything" capability you'd want doesn't really exist yet — search today only looks inside a small internal notebook, not GitHub/Vercel/Supabase/the actual codebase. END_USER_ENGINE (the thing that would let your paying customers talk to VERIDIAN directly) has zero code written for it. This plan says: fix the alarm system first (days, not weeks), let the two workflows already running (`UNCOMPLICATE_UNDUPLICATE_TASK`, `TWO_ENGINE_TASK`) finish their piece, then build the search layer and the customer-facing engine on top, and don't let real customers in until it's been proven the box can handle the load — which it hasn't been tested for yet.

**Decisions that need the Owner, not this document:**
1. Clear the current EMERGENCY_STOP (or decide it should stay frozen pending a fix) — this document intentionally did not touch it.
2. Pick systemd-service vs. restored-cron for the dispatch trigger (Phase 0 step 2) — either works, needs a call.
3. Pick Path A (move search index into Supabase/Postgres) vs. Path B (keep SQLite, add a fail-closed wrapper) for the search/registry visibility filter (§2.2) — real tradeoff between build effort and enforcement strength.
4. Decide what alerting channel replaces the dead-letter `ATTENTION.md` file (push notification? email? something else?).
5. Confirm the 2026-08-05 AI-provider deadline is still real, and what happens automatically if it passes with END_USER_ENGINE still unbuilt (Phase 6).
6. Set an actual cost ceiling number for end-user AI usage once there's real volume data to size it against (item 7 above) — this document deliberately did not invent a number.

---

## 7. What remains genuinely open, stated once more without hedging

This design does not claim 100% certainty anywhere load and real-world behavior are involved: **whether the dispatch spine survives real concurrent load, what the right per-tenant ceiling number is, whether the `disk_io=100.0` reading is itself trustworthy, and whether the AWS SaaS control-plane pattern actually fits VERIDIAN's shape — none of these can be resolved on paper.** They require running code under real conditions that don't exist yet (no end users, no load test performed, no independent metric corroboration attempted). Marking them open is the honest output of this exercise, not a gap in the exercise itself.
