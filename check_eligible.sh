#!/bin/bash

TASK_DIR="/opt/veridian/ai-os/tasks"

echo "Checking which tasks have terminal status and workspaces..."
echo ""

count=0
eligible=0

for task_path in $(find /opt/veridian/ai-os/tasks -maxdepth 1 -type d -name "task-*" | sort); do
    task_name=$(basename "$task_path")
    yaml="$task_path/task.yaml"
    ws="$task_path/workspace"
    
    count=$((count + 1))
    
    # Get status
    if [ -f "$yaml" ]; then
        status=$(timeout 2 grep "^status:" "$yaml" | cut -d: -f2 | xargs)
    else
        status="NO_YAML"
    fi
    
    # Check if workspace exists
    if [ ! -d "$ws" ]; then
        continue
    fi
    
    # Check if status is terminal
    case "$status" in
        completed|completed_unmerged|failed|killed|rejected_duplicate)
            eligible=$((eligible + 1))
            ws_size=$(du -sb "$ws" 2>/dev/null | awk '{print int($1/1024/1024)}')
            echo "✓ $task_name [$status] ${ws_size}MB"
            ;;
    esac
done

echo ""
echo "Summary: $count tasks checked, $eligible have terminal status + workspace"
