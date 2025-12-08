#!/bin/bash

# Read JSON input once
input=$(cat)

# Get git info from existing script
git_info=$(echo "$input" | bash /home/vscode/project/.claude/statusline-command.sh)

# Get context percentage from ccstatusline (uses ~/.config/ccstatusline/settings.json)
context_pct=$(echo "$input" | npx ccstatusline 2>/dev/null)

# Combine outputs
if [ -n "$context_pct" ]; then
    printf '%s | %s' "$git_info" "$context_pct"
else
    printf '%s' "$git_info"
fi
