#!/bin/bash
# Create a new branch with a consistent type/description naming convention.
#
# Usage:
#   git:branch                          # Interactive: pick type, enter description
#   git:branch feat "add login page"    # Direct: type + description
#   git:branch fix login-bug            # Direct: already slugified
#
# Alias: git:branch (via symlink in /usr/local/bin)

set -e

TYPES=(feat fix improvement chore refactor spec docs bugfix)

slugify() {
    echo "$*" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g; s/--*/-/g; s/^-//; s/-$//'
}

branch_type="$1"
shift 2>/dev/null || true
description="$*"

# Interactive type selection if not provided or invalid
if [ -z "$branch_type" ] || ! printf '%s\n' "${TYPES[@]}" | grep -qx "$branch_type"; then
    if [ -n "$branch_type" ]; then
        # First arg wasn't a valid type — treat everything as description
        description="$branch_type $description"
        description="${description% }"
    fi

    echo "Branch type:"
    for i in "${!TYPES[@]}"; do
        printf "  %d) %s\n" $((i + 1)) "${TYPES[$i]}"
    done
    echo ""
    read -r -p "Pick [1-${#TYPES[@]}]: " choice

    if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt "${#TYPES[@]}" ]; then
        echo "Invalid choice."
        exit 1
    fi
    branch_type="${TYPES[$((choice - 1))]}"
fi

# Get description if not provided
if [ -z "$description" ]; then
    read -r -p "Description (short, e.g. 'add login page'): " description
    if [ -z "$description" ]; then
        echo "Description required."
        exit 1
    fi
fi

slug=$(slugify "$description")
branch_name="${branch_type}/${slug}"

echo ""
echo "Creating branch: $branch_name (from develop)"
read -r -p "Continue? [Y/n]: " confirm
if [[ "$confirm" =~ ^[Nn] ]]; then
    echo "Aborted."
    exit 1
fi

git fetch origin develop --quiet
git checkout -b "$branch_name" origin/develop

echo ""
echo "Switched to new branch '$branch_name'"
