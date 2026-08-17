#!/usr/bin/env python3
"""
IMPORTANT CORRECTION: workspace/progress/*.md is NOT unique per task
directory -- some workspace-priming step copies many *other* tasks' real
progress/<their-id>.md files into each new task's own workspace/progress/
directory (observed: task-20260816-120207's checkout contains
progress/task-20260814-095552-....md, i.e. a DIFFERENT task's file). Naively
attributing that content to the containing task directory misattributes
real evidence to the wrong task id.

This script scans every task workspace's workspace/progress/*.md once,
extracts the task id the filename names, and keeps the longest (most
complete) version of each. The result is a global, correctly-attributed
corpus: real_task_id -> its own real progress content, usable regardless
of which container directory it was physically found in.
"""
import json
import os

TASKS_DIR = "/opt/veridian/ai-os/tasks"

def read_file_safe(path, limit=200000):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read(limit)
    except Exception:
        return ""

def main():
    corpus = {}  # task_id (from filename, minus .md) -> content
    names = sorted(os.listdir(TASKS_DIR))
    scanned_dirs = 0
    found_files = 0
    for name in names:
        prog_dir = os.path.join(TASKS_DIR, name, "workspace", "progress")
        if not os.path.isdir(prog_dir):
            continue
        scanned_dirs += 1
        try:
            fns = os.listdir(prog_dir)
        except Exception:
            continue
        for fn in fns:
            if not fn.endswith(".md"):
                continue
            found_files += 1
            tid = fn[:-3]
            content = read_file_safe(os.path.join(prog_dir, fn))
            if tid not in corpus or len(content) > len(corpus[tid]):
                corpus[tid] = content

    print(f"scanned {scanned_dirs} task dirs with a progress/ subdir, {found_files} file instances, {len(corpus)} unique task ids")
    with open("progress_corpus.json", "w") as f:
        json.dump(corpus, f)

if __name__ == "__main__":
    main()
