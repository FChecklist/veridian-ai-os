#!/usr/bin/env python3
"""
Corrected index build: uses the deduped, correctly-attributed progress
corpus (progress_corpus.json) instead of blindly reading whatever
workspace/progress/*.md files happen to be physically present in a given
task's own workspace checkout (which was shown to include OTHER tasks'
progress files via a workspace-priming/resync step).
"""
import json
import os
import re
import yaml

TASKS_DIR = "/opt/veridian/ai-os/tasks"

corpus = json.load(open("progress_corpus.json"))

def read_file_safe(path, limit=200000):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read(limit)
    except Exception:
        return ""

def main():
    entries = []
    names = sorted(os.listdir(TASKS_DIR))
    for name in names:
        d = os.path.join(TASKS_DIR, name)
        if not os.path.isdir(d):
            continue
        task_yaml_path = os.path.join(d, "task.yaml")
        title = ""
        status = ""
        branch = ""
        task_id = name
        if os.path.exists(task_yaml_path):
            raw = read_file_safe(task_yaml_path)
            try:
                y = yaml.safe_load(raw)
                if isinstance(y, dict):
                    title = y.get("title", "") or ""
                    status = y.get("status", "") or ""
                    branch = y.get("branch", "") or ""
                    task_id = y.get("id", name) or name
            except Exception:
                m = re.search(r'^title:\s*(.+)$', raw, re.M)
                if m:
                    title = m.group(1).strip()
                m = re.search(r'^status:\s*(\S+)', raw, re.M)
                if m:
                    status = m.group(1).strip()
                m = re.search(r'^branch:\s*(\S+)', raw, re.M)
                if m:
                    branch = m.group(1).strip()

        prompt_txt = read_file_safe(os.path.join(d, "prompt.txt"))
        top_progress_md = read_file_safe(os.path.join(d, "workspace", "PROGRESS.md"))
        own_progress = corpus.get(task_id, "") or corpus.get(name, "")

        blob = "\n".join([name, title, branch, prompt_txt, top_progress_md, own_progress]).lower()

        entries.append({
            "dirname": name,
            "id": task_id,
            "title": title,
            "status": status,
            "branch": branch,
            "has_prompt": bool(prompt_txt),
            "has_own_progress_corpus_entry": bool(own_progress),
            "blob_len": len(blob),
            "_blob": blob,
        })

    with open("task_index2.json", "w") as f:
        json.dump(entries, f)
    n_with_progress = sum(1 for e in entries if e["has_own_progress_corpus_entry"])
    print(f"Indexed {len(entries)} task directories, {n_with_progress} with a correctly-attributed progress corpus entry")

if __name__ == "__main__":
    main()
