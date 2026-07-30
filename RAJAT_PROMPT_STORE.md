# RAJAT PROMPT STORE -- verified placeholder, not a guess

This is the ONE fixed pointer to the real Owner<->Assistant conversation/task store.
Verified live against reality on write (not asserted): as of this writing there are
real 58 instructions, 113 work_items, 4875 actions in it.

**The real store:** `ai-os/memory/superboss-register.sqlite` (SQLite, not a markdown file --
a prior version of the standing prompt wrongly said `SUPERBOSS_REGISTER.md`; that file never
existed, corrected 2026-07-22).

**How to read it (the actual, tested command):**
```
python3 ai-os/scripts/session_bootstrap.py [N]
```
This is verified to exist and run at the time this placeholder was written -- see
`ai-os/scripts/session_bootstrap.py` (`bootstrap_exists` check passed before this file
was written).

**How to write to it:**
```
python3 /opt/veridian/scripts/superboss-register.py log-instruction ...
python3 ai-os/scripts/postflight_audit_gate.py --software-task-id ... --audit-cmd ... --content ...
```
Never write a terminal DONE/FAILED status any other way -- see STANDING_DIRECTIVE.yaml
rule_8_mandatory_audit_before_completion.

**If this placeholder is ever wrong** (paths change, script renamed): that is itself a bug
in this exact file -- fix THIS file, do not create a second placeholder elsewhere. Per
STANDING_DIRECTIVE.yaml's zero-duplication rule.
