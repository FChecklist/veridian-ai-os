#!/usr/bin/env python3
"""
Step 0 of the pipeline: parse the real output of
`python3 /opt/veridian/scripts/queue-manager.py list` into a
{truncated_task_id: {status, priority, paused, created}} map.

queue-manager.py's own list command truncates the ID column to 46 chars for
display (see its source: `t['id'][:46]`), so the keys here are that same
46-char-truncated form -- guaranteed to be a literal substring of a real
line in the command's real output, which is what SUCCESS_CRITERIA requires
for a citable matching_task_id.

Run:
  python3 /opt/veridian/scripts/queue-manager.py list > queue_list_raw.txt
  python3 parse_queue.py
"""
import json
import re

status_map = {}
with open("queue_list_raw.txt") as f:
    for line in f:
        line = line.rstrip("\n")
        m = re.match(r'^\s{2}(task-\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', line)
        if m:
            tid, status, priority, paused, created = m.groups()
            status_map[tid] = {"status": status, "priority": priority, "paused": paused, "created": created}

print(f"Parsed {len(status_map)} real post-dispatch task rows from queue-manager.py list")
with open("queue_status_map.json", "w") as f:
    json.dump(status_map, f)
