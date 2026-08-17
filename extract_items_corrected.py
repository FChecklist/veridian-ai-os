#!/usr/bin/env python3
import json

d = json.load(open('/opt/veridian/ai-os/tasks/task-20260817-141839-fix-fabricated-pendency-list-self-audit/workspace/master_list.json'))
items = d["items"]
target = [it for it in items if it.get("recommended_action") in ("MERGE", "REVISE", "IMPLEMENT")]
print("total corrected target items:", len(target))
from collections import Counter
print(Counter(it["recommended_action"] for it in target))
with open("target_items_corrected.json", "w") as f:
    json.dump(target, f, indent=2)
