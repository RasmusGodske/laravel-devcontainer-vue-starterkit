#!/bin/bash
# Run code review using reldo
#
# This script wraps the reldo CLI tool with project defaults.
# It automatically uses the project's reldo configuration.
#
# Usage:
#   ./devtools/review/code.sh "Review the changes for: feature description"
#   ./devtools/review/code.sh "Review app/Models/User.php"
#
# Alias: review:code (via symlink in /usr/local/bin)
#
# Arguments:
#   PROMPT        Review prompt (required, use '-' for stdin)
#
# Options:
#   --json        Output result as JSON
#   --verbose     Enable verbose logging
#   --no-log      Disable session logging
#   --exit-code   Exit with code 1 if review fails (for CI)
#
# Examples:
#   review:code "Review the authentication changes"
#   review:code "Review: Adding user metrics" --exit-code
#   review:code "Review app/Services/" --verbose

set -e

# Resolve symlinks to get actual script location
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_DIR"

# Check if reldo is installed
if ! command -v reldo &> /dev/null; then
    echo "Error: reldo is not installed."
    echo ""
    echo "Install it with:"
    echo "  uv tool install reldo"
    echo ""
    echo "Or from GitHub for latest:"
    echo "  uv tool install git+https://github.com/RasmusGodske/reldo.git"
    exit 1
fi

# Check if config exists
CONFIG_PATH=".reldo/settings.json"
if [ ! -f "$CONFIG_PATH" ]; then
    echo "Error: reldo config not found at $CONFIG_PATH"
    exit 1
fi

# Run reldo with project config
exec reldo review --config "$CONFIG_PATH" "$@"
