# veridian-ai-os — historical snapshot (frozen)

> **⚠️ This repo is a frozen historical snapshot, not a live system.**
> It is a version-controlled copy of `/opt/veridian/ai-os` as it existed on
> the **VERIDIAN-DEV Hetzner server (167.233.220.35)**, which was
> **permanently deleted on 2026-08-25**. `DIRECTIVE.yaml` and every other
> `ACTIVE`-status doc in this repo still describe that server as the live
> execution node — they are **not** current. All real development now
> happens directly on the developer's laptop; there is no server-based
> control plane anymore.

Last real commit: 2026-08-18 (before the server deletion). Nothing in this
repo has been updated since, and nothing should be treated as an
instruction for a currently-running system.

## What's actually in here

~5,000 tracked files: dated YAML/JSON/Markdown status snapshots, phase
plans, and audit reports produced by the old server-based orchestration
system, spanning roughly 2026-07-21 through 2026-08-18. It's kept as an
audit trail of what that system believed/produced at the time — useful for
historical reference, not as a source of current configuration or
instructions.

## Where the real thing lives now

Current VERIDIAN AI OS development happens in
[FChecklist/compliance-tracker](https://github.com/FChecklist/compliance-tracker),
worked on directly (no server, no proxy layer).

---
*Added 2026-09-01 as part of a code-quality inspection pass (see
`public.code_quality_inspection_findings` in the `verdian-ai` Supabase
project) that flagged this repo's docs as actively misleading about
current infrastructure.*
