#!/bin/bash

# Execute workspace deletion for all eligible tasks
# Follows UMR-20260807-075748-3f33 procedure

TASK_DIR="/opt/veridian/ai-os/tasks"
REPORT_FILE="deletion_report.txt"

echo "=== DISK RECLAMATION: EXECUTION PHASE ===" | tee "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"
echo "Starting deletion at: $(date -u '+%Y-%m-%dT%H:%M:%SZ')" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Record before state
echo "BEFORE STATE:" | tee -a "$REPORT_FILE"
df -h / | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

deleted_count=0
deleted_bytes=0

# Process each task directory
for task_path in $(find /opt/veridian/ai-os/tasks -maxdepth 1 -type d -name "task-*" | sort); do
    task_name=$(basename "$task_path")
    yaml="$task_path/task.yaml"
    ws="$task_path/workspace"

    # Quick check: does task.yaml exist and have terminal status?
    if [ ! -f "$yaml" ]; then
        continue
    fi

    status=$(timeout 2 grep "^status:" "$yaml" 2>/dev/null | cut -d: -f2 | xargs || echo "")

    # Check if status is terminal
    case "$status" in
        completed|completed_unmerged|failed|killed|rejected_duplicate)
            # Check if workspace exists
            if [ -d "$ws" ]; then
                # Get size before deletion
                ws_size=$(du -sb "$ws" 2>/dev/null | awk '{print $1}' || echo "0")

                # Delete the workspace
                rm -rf "$ws" 2>/dev/null

                if [ $? -eq 0 ]; then
                    deleted_count=$((deleted_count + 1))
                    deleted_bytes=$((deleted_bytes + ws_size))
                    ws_size_mb=$((ws_size / 1024 / 1024))
                    echo "✓ DELETED: $task_name [$status] ${ws_size_mb}MB" | tee -a "$REPORT_FILE"
                else
                    echo "✗ FAILED:  $task_name [deletion error]" | tee -a "$REPORT_FILE"
                fi
            fi
            ;;
    esac
done

echo "" | tee -a "$REPORT_FILE"
echo "AFTER STATE:" | tee -a "$REPORT_FILE"
df -h / | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Calculate summary
deleted_gb=$(echo "scale=2; $deleted_bytes / 1024 / 1024 / 1024" | bc)
deleted_mb=$((deleted_bytes / 1024 / 1024))

echo "=== DELETION SUMMARY ===" | tee -a "$REPORT_FILE"
echo "Workspaces deleted: $deleted_count" | tee -a "$REPORT_FILE"
echo "Total bytes reclaimed: $deleted_bytes ($deleted_gb GB)" | tee -a "$REPORT_FILE"
echo "Completion time: $(date -u '+%Y-%m-%dT%H:%M:%SZ')" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Show report file
echo "Report saved to: $REPORT_FILE"
echo ""
echo "First 50 lines of report:"
head -50 "$REPORT_FILE"
