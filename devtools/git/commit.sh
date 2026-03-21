#!/bin/bash
# Commit staged changes, optionally generating a message with Claude.
#
# Usage:
#   git:commit                      # Generate commit message from staged diff
#   git:commit "fix: login bug"     # Use provided message
#   git:commit -y                   # Generate and commit without confirmation
#
# Alias: git:commit (via symlink in /usr/local/bin)

AUTO_CONFIRM=false
ARGS=()
for arg in "$@"; do
    if [ "$arg" = "-y" ] || [ "$arg" = "--yes" ]; then
        AUTO_CONFIRM=true
    else
        ARGS+=("$arg")
    fi
done

commit_message="${ARGS[*]}"

# Ensure there are staged changes
if git diff --cached --quiet; then
    echo "Nothing staged. Use 'git add' to stage files first."
    exit 1
fi

if [ -n "$commit_message" ]; then
    git commit -m "$commit_message"
    exit $?
fi

# Generate commit message with Claude
spinner_pid=""

stop_spinner() {
    if [ -n "$spinner_pid" ]; then
        kill "$spinner_pid" 2>/dev/null || true
        wait "$spinner_pid" 2>/dev/null || true
        spinner_pid=""
        printf "\r\033[K"
    fi
}

start_spinner() {
    local spinner="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    (
        while true; do
            for (( i=0; i<${#spinner}; i++ )); do
                printf "\r${spinner:$i:1} Generating commit message..."
                sleep 0.1
            done
        done
    ) &
    spinner_pid=$!
}

trap stop_spinner EXIT INT

start_spinner

diff_input=$(printf "=== Summary ===\n%s\n\n=== Diff (truncated) ===\n%s" \
    "$(git diff --cached --stat)" \
    "$(git diff --cached | head -c 50000)")

commit_message=$(echo "$diff_input" | env -u CLAUDECODE claude -p \
    "Write a single-line commit message for this diff. Output ONLY the message, no quotes, no explanation, no markdown." 2>/dev/null)

stop_spinner
trap - EXIT INT

# Trim leading/trailing whitespace and blank lines
commit_message=$(echo "$commit_message" | sed '/^$/d' | head -1 | xargs)

if [ -z "$commit_message" ]; then
    echo "Failed to generate commit message."
    exit 1
fi

echo "Message: $commit_message"

if [ "$AUTO_CONFIRM" = false ]; then
    echo ""
    read -r -p "Commit with this message? [Y/n/e(dit)]: " confirm

    case "$confirm" in
        [Nn])
            echo "Aborted."
            exit 1
            ;;
        [Ee])
            read -r -e -p "Edit message: " -i "$commit_message" commit_message
            ;;
    esac
fi

git commit -m "$commit_message"
