#!/bin/bash

# Read JSON input
input=$(cat)

# Extract values from JSON
cwd=$(echo "$input" | jq -r '.workspace.current_dir')
model=$(echo "$input" | jq -r '.model.display_name')
cost=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')

# Format cost
if [ "$cost" != "0" ] && [ "$cost" != "null" ]; then
    cost_formatted=$(printf "$%.4f" "$cost")
else
    cost_formatted="\$0.00"
fi

# Git information
if git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
    branch=$(git -C "$cwd" --no-optional-locks rev-parse --abbrev-ref HEAD 2>/dev/null)
    gitinfo=$(printf '\033[01;32m%s\033[00m' "$branch")
else
    gitinfo=""
fi

# Format: [Model] directory | branch | $cost
dir_name=$(basename "$cwd")
printf '\033[0;35m[%s]\033[00m \033[01;36m%s\033[00m | %s | \033[0;33m%s\033[0m' "$model" "$dir_name" "$gitinfo" "$cost_formatted"
