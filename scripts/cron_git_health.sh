#!/bin/bash
# Git health monitoring script for cron
# Add to crontab with: */15 * * * * /path/to/this/script

cd "$(dirname "$0")/.."

# Log file
LOG_FILE="logs/git_health.log"

# Timestamp
echo "$(date): Checking git health..." >> "$LOG_FILE"

# Run health check
python3 scripts/monitor_git_sync.py --check >> "$LOG_FILE" 2>&1

# Check for critical issues (more than 5 commits ahead)
COMMITS_AHEAD=$(git rev-list --count HEAD ^origin/main 2>/dev/null || echo 0)

if [ "$COMMITS_AHEAD" -gt 5 ]; then
    echo "$(date): CRITICAL - $COMMITS_AHEAD commits ahead, attempting sync..." >> "$LOG_FILE"
    python3 scripts/monitor_git_sync.py --sync >> "$LOG_FILE" 2>&1
fi

echo "$(date): Health check complete" >> "$LOG_FILE"