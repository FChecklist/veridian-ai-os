#!/usr/bin/env python3
"""
Disk reclamation for task workspace directories.
Follows the exact procedure from UMR-20260807-075748-3f33.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from collections import defaultdict
import yaml

TASK_DIR = Path('/opt/veridian/ai-os/tasks')
TERMINAL_STATUSES = {'completed', 'completed_unmerged', 'failed', 'killed', 'rejected_duplicate'}

def get_disk_usage(path):
    """Get size of directory in bytes."""
    try:
        result = subprocess.run(['du', '-sb', str(path)], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return int(result.stdout.split()[0])
    except Exception as e:
        print(f"Error getting size for {path}: {e}")
    return 0

def check_task_yaml(task_dir):
    """Check if task.yaml has terminal status."""
    task_yaml = task_dir / 'task.yaml'
    if not task_yaml.exists():
        return False, "No task.yaml"

    try:
        with open(task_yaml) as f:
            data = yaml.safe_load(f)
            status = data.get('status', '')
            if status in TERMINAL_STATUSES:
                return True, f"Terminal ({status})"
            else:
                return False, f"Not terminal ({status})"
    except Exception as e:
        return False, f"Error reading task.yaml: {e}"

def check_systemd_unit(task_name):
    """Check if associated systemd unit is inactive."""
    try:
        result = subprocess.run(
            ['systemctl', '--user', 'is-active', task_name],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            # Unit doesn't exist or is not active
            state = result.stdout.strip() or 'unknown'
            if state in ['inactive', 'unknown', 'not-found']:
                return True, f"Inactive/not-found ({state})"
            else:
                return False, f"Active/other state ({state})"
        return False, "Unit exists and active"
    except Exception as e:
        # If we can't check, assume it's safe (unit likely doesn't exist)
        return True, "Systemd check skipped (not resolvable)"

def check_git_clean(workspace_dir):
    """Check if workspace is clean git repo with no uncommitted changes."""
    if not workspace_dir.exists():
        return False, "No workspace directory"

    if not (workspace_dir / '.git').exists():
        return False, "Not a git repository"

    try:
        result = subprocess.run(
            ['git', '-C', str(workspace_dir), 'status', '--porcelain'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            if result.stdout.strip():
                return False, f"Uncommitted changes ({len(result.stdout.splitlines())} files)"
            else:
                return True, "Clean"
        else:
            return False, "Git status check failed"
    except Exception as e:
        return False, f"Error checking git status: {e}"

def check_upstream_status(workspace_dir):
    """Check if current branch has upstream and no unpushed commits."""
    try:
        # Check if there's an upstream configured
        result = subprocess.run(
            ['git', '-C', str(workspace_dir), 'rev-parse', '--abbrev-ref', '@{u}'],
            capture_output=True, text=True, timeout=5
        )

        if result.returncode != 0:
            # No upstream configured
            return False, "No upstream branch"

        # Check for unpushed commits
        result = subprocess.run(
            ['git', '-C', str(workspace_dir), 'log', '@{u}..HEAD', '--oneline'],
            capture_output=True, text=True, timeout=5
        )

        if result.returncode == 0:
            if result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                return False, f"Unpushed commits ({len(lines)})"
            else:
                return True, "Up to date"
        else:
            return False, "Upstream check failed"
    except Exception as e:
        return False, f"Error checking upstream: {e}"

def evaluate_task_dir(task_dir):
    """Evaluate a single task directory."""
    task_name = task_dir.name
    workspace_dir = task_dir / 'workspace'

    results = {
        'task_dir': task_name,
        'path': str(task_dir),
        'workspace_size': 0,
        'delete': False,
        'reasons': []
    }

    # Get workspace size if it exists
    if workspace_dir.exists():
        results['workspace_size'] = get_disk_usage(workspace_dir)

    # Check condition 1: task.yaml has terminal status
    yaml_ok, yaml_reason = check_task_yaml(task_dir)
    if not yaml_ok:
        results['reasons'].append(f"[task.yaml] {yaml_reason}")
    else:
        results['reasons'].append(f"[task.yaml] ✓ {yaml_reason}")

    # Check condition 2: systemd unit is inactive
    systemd_ok, systemd_reason = check_systemd_unit(task_name)
    if not systemd_ok:
        results['reasons'].append(f"[systemd] {systemd_reason}")
    else:
        results['reasons'].append(f"[systemd] ✓ {systemd_reason}")

    # Check condition 3: workspace is clean git repo
    git_ok, git_reason = check_git_clean(workspace_dir)
    if not git_ok:
        results['reasons'].append(f"[git-clean] {git_reason}")
    else:
        results['reasons'].append(f"[git-clean] ✓ {git_reason}")

    # Check condition 4: upstream status
    upstream_ok, upstream_reason = check_upstream_status(workspace_dir)
    if not upstream_ok:
        results['reasons'].append(f"[upstream] {upstream_reason}")
    else:
        results['reasons'].append(f"[upstream] ✓ {upstream_reason}")

    # All conditions must be met
    if yaml_ok and systemd_ok and git_ok and upstream_ok and workspace_dir.exists():
        results['delete'] = True

    return results

def main():
    print("=" * 100)
    print("DISK RECLAMATION: Task Workspace Analysis")
    print("=" * 100)

    # Get all task directories
    task_dirs = sorted([d for d in TASK_DIR.iterdir() if d.is_dir() and d.name.startswith('task-')])

    print(f"\nFound {len(task_dirs)} task directories")
    print(f"\nEvaluating each directory for deletion eligibility...")
    print()

    results = []
    for task_dir in task_dirs:
        result = evaluate_task_dir(task_dir)
        results.append(result)

    # Summarize
    deletable = [r for r in results if r['delete']]
    skipped = [r for r in results if not r['delete']]

    print("\n" + "=" * 100)
    print(f"SUMMARY: {len(deletable)} deletable, {len(skipped)} to skip")
    print("=" * 100)

    # Detailed table
    print("\nDETAILED EVALUATION TABLE:")
    print("-" * 100)
    print(f"{'Task Directory':<50} {'Decision':<10} {'Size':<15} {'Reason'}")
    print("-" * 100)

    for result in results:
        decision = "DELETE" if result['delete'] else "SKIP"
        size_str = f"{result['workspace_size'] / (1024**3):.2f}GB" if result['workspace_size'] > 0 else "N/A"
        reason = "; ".join(result['reasons'])
        print(f"{result['task_dir']:<50} {decision:<10} {size_str:<15} {reason}")

    # Calculate totals
    total_deletable_bytes = sum(r['workspace_size'] for r in deletable)
    total_deletable_gb = total_deletable_bytes / (1024**3)

    print("-" * 100)
    print(f"\nDeletable workspaces: {len(deletable)}")
    print(f"Skipped: {len(skipped)}")
    print(f"Total bytes to reclaim: {total_deletable_bytes:,} ({total_deletable_gb:.2f} GB)")
    print()

    # Save results for deletion phase
    with open('/opt/veridian/ai-os/tasks/task-20260817-184059-reclaim-terminal-task-workspace-disk-spa/workspace/reclaim_results.json', 'w') as f:
        json.dump({
            'timestamp': str(subprocess.run(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'], capture_output=True, text=True).stdout.strip()),
            'task_dirs_total': len(task_dirs),
            'deletable_count': len(deletable),
            'skip_count': len(skipped),
            'total_bytes_reclaimable': total_deletable_bytes,
            'total_gb_reclaimable': total_deletable_gb,
            'deletable': deletable,
            'skipped': skipped
        }, f, indent=2)

    print("Results saved to reclaim_results.json")

if __name__ == '__main__':
    main()
