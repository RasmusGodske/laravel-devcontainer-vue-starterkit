#!/bin/bash
# Create a pull request with an AI-generated or user-provided description.
#
# Usage:
#   git:pr                          # Generate title + description from commits
#   git:pr -y                       # Generate and create without confirmation
#   git:pr -m "My description"      # Use provided description (title still generated)
#   git:pr -t "My title"            # Use provided title (description still generated)
#   git:pr -t "Title" -m "Desc"     # Use both provided
#   git:pr --base main              # Target a different base branch (default: develop)
#
# Alias: git:pr (via symlink in /usr/local/bin)

BASE_BRANCH="develop"
AUTO_CONFIRM=false
USER_TITLE=""
USER_BODY=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -y|--yes)        AUTO_CONFIRM=true; shift ;;
        -t|--title)      USER_TITLE="$2"; shift 2 ;;
        -m|--message)    USER_BODY="$2"; shift 2 ;;
        --base)          BASE_BRANCH="$2"; shift 2 ;;
        *)               echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Ensure we're not on the base branch
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$current_branch" = "$BASE_BRANCH" ]; then
    echo "Already on $BASE_BRANCH. Switch to a feature branch first."
    exit 1
fi

# Check for existing PR
existing_pr=$(gh pr view --json url --jq '.url' 2>/dev/null)
if [ -n "$existing_pr" ]; then
    echo "PR already exists: $existing_pr"
    exit 1
fi

# Ensure branch is pushed
if ! git rev-parse --abbrev-ref --symbolic-full-name "@{u}" >/dev/null 2>&1; then
    echo "Pushing branch to origin..."
    git push -u origin "$current_branch"
fi

# Check if remote is up to date
local_sha=$(git rev-parse HEAD)
remote_sha=$(git rev-parse "@{u}" 2>/dev/null)
if [ "$local_sha" != "$remote_sha" ]; then
    echo "Local commits not pushed. Pushing..."
    git push origin HEAD
fi

# Gather commit log and diff stat for context
commit_log=$(git log "$BASE_BRANCH"..HEAD --pretty=format:"%s" 2>/dev/null)
if [ -z "$commit_log" ]; then
    echo "No commits ahead of $BASE_BRANCH. Nothing to create a PR for."
    exit 1
fi

diff_stat=$(git diff "$BASE_BRANCH"...HEAD --stat 2>/dev/null)

# Generate title and body if not provided
needs_generation=false
if [ -z "$USER_TITLE" ] || [ -z "$USER_BODY" ]; then
    needs_generation=true
fi

if [ "$needs_generation" = true ]; then
    spinner_pid=""

    stop_spinner() {
        if [ -n "$spinner_pid" ]; then
            kill "$spinner_pid" 2>/dev/null || true
            wait "$spinner_pid" 2>/dev/null || true
            spinner_pid=""
            printf "\r\033[K"
        fi
    }

    trap stop_spinner EXIT INT

    local_spinner="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    (
        while true; do
            for (( i=0; i<${#local_spinner}; i++ )); do
                printf "\r${local_spinner:$i:1} Generating PR description..."
                sleep 0.1
            done
        done
    ) &
    spinner_pid=$!

    context=$(printf "=== Branch ===\n%s\n\n=== Commits ===\n%s\n\n=== Diff stat ===\n%s" \
        "$current_branch" \
        "$commit_log" \
        "$diff_stat")

    prompt_parts=""
    if [ -z "$USER_TITLE" ] && [ -z "$USER_BODY" ]; then
        prompt_parts="Generate a PR title and body."
    elif [ -z "$USER_TITLE" ]; then
        prompt_parts="Generate ONLY a PR title. The body is already provided."
    else
        prompt_parts="Generate ONLY a PR body. The title is already provided: $USER_TITLE"
    fi

    ai_output=$(echo "$context" | env -u CLAUDECODE claude -p "$prompt_parts

Format your response EXACTLY as:
TITLE: <single line title, under 70 chars>
BODY:
<markdown body with a ## Summary section listing key changes as bullet points>

Output ONLY this format, no explanation, no wrapping quotes." 2>/dev/null)

    stop_spinner
    trap - EXIT INT

    ai_output=$(echo "$ai_output" | sed '/^$/d')

    if [ -z "$ai_output" ]; then
        echo "Failed to generate PR description."
        exit 1
    fi

    if [ -z "$USER_TITLE" ]; then
        USER_TITLE=$(echo "$ai_output" | grep '^TITLE:' | sed 's/^TITLE: *//')
    fi
    if [ -z "$USER_BODY" ]; then
        USER_BODY=$(echo "$ai_output" | sed -n '/^BODY:/,$ p' | sed '1s/^BODY: *//' | sed '1{/^$/d}')
    fi
fi

# Fallback if parsing failed
if [ -z "$USER_TITLE" ]; then
    USER_TITLE="$current_branch"
fi

# Display what we're about to create
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  PR: $USER_TITLE"
echo "  $current_branch -> $BASE_BRANCH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "$USER_BODY"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$AUTO_CONFIRM" = false ]; then
    echo ""
    read -r -p "Create this PR? [Y/n]: " confirm
    if [[ "$confirm" =~ ^[Nn] ]]; then
        echo "Aborted."
        exit 1
    fi
fi

pr_url=$(gh pr create \
    --base "$BASE_BRANCH" \
    --title "$USER_TITLE" \
    --body "$USER_BODY" 2>&1)

if [ $? -ne 0 ]; then
    echo "Failed to create PR: $pr_url"
    exit 1
fi

echo ""
echo "PR created: $pr_url"
