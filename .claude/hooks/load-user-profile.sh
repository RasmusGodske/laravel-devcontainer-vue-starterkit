#!/bin/bash
# Load user profile at session start
#
# This hook reads .claude-user-profile.md (if it exists) and injects
# its content into the conversation context. This allows users to
# customize how Claude interacts with them based on their skill level.
#
# If no profile exists, it instructs Claude to run the /setup-profile skill.
#
# The profile file is not committed to the repository - each user
# can create their own by running the /setup-profile skill.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
PROFILE_FILE="$PROJECT_ROOT/.claude-user-profile.md"

# If no profile exists, instruct Claude to run the setup skill
if [ ! -f "$PROFILE_FILE" ]; then
    cat << 'EOF'
# No User Profile Found

The user has not set up their profile yet. Before doing anything else, you should:

1. Warmly welcome the user to their project
2. Run the `/setup-profile` skill to help them set up their preferences

This only needs to happen once - after they complete the setup, this message won't appear again.
EOF
    exit 0
fi

# Read and output the profile content
cat "$PROFILE_FILE"

exit 0
