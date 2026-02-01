#!/bin/bash
# Run ESLint for JavaScript/Vue/TypeScript code quality
#
# This script runs ESLint to check for code quality issues.
# For TypeScript type checking, use lint:ts instead.
#
# Usage:
#   ./devtools/lint/js.sh                              # Lint all frontend files
#   ./devtools/lint/js.sh resources/js/Pages/Login.vue # Lint specific file
#   ./devtools/lint/js.sh resources/js/Pages/*.vue     # Lint multiple files
#
# Alias: lint:js (via symlink in /usr/local/bin)
#
# Options:
#   --no-lumby    Skip AI diagnosis on failure

set -e

# Resolve symlinks to get actual script location
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_DIR"

# Parse options
USE_LUMBY=true
FILES=()

for arg in "$@"; do
    case $arg in
        --no-lumby)
            USE_LUMBY=false
            ;;
        --help|-h)
            echo "Usage: lint:js [OPTIONS] [FILES...]"
            echo ""
            echo "Run ESLint for JavaScript/Vue/TypeScript code quality"
            echo ""
            echo "Options:"
            echo "  --no-lumby     Skip AI diagnosis on failure"
            echo "  --help, -h     Show this help message"
            echo ""
            echo "Examples:"
            echo "  lint:js                                # Lint all files"
            echo "  lint:js resources/js/Pages/Login.vue   # Lint specific file"
            echo "  lint:js resources/js/Pages/*.vue       # Lint multiple files"
            echo ""
            echo "For TypeScript type checking, use: lint:ts"
            exit 0
            ;;
        *)
            FILES+=("$arg")
            ;;
    esac
done

# Auto-disable Lumby in CI environments when ANTHROPIC_API_KEY is not set
# When the API key is available, Lumby can authenticate Claude Code
if [ "${CI:-false}" = "true" ] && [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    USE_LUMBY=false
fi

# Helper function to run command with optional lumby
run_cmd() {
    if [ "$USE_LUMBY" = "true" ]; then
        lumby -- "$@"
    else
        "$@"
    fi
}

# Capture exit code to save tarnished checkpoint on success
set +e
if [ ${#FILES[@]} -eq 0 ]; then
    # No files specified - lint everything
    echo "=== Running ESLint ==="
    run_cmd npm run lint
else
    # Files specified - lint only those files
    echo "=== Running ESLint on specified files ==="
    printf '  %s\n' "${FILES[@]}"
    echo ""
    run_cmd npx eslint "${FILES[@]}"
fi
exit_code=$?
set -e

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "ESLint: PASSED"
    # Save tarnished checkpoint on success
    tarnished save lint:js 2>/dev/null || true
fi

exit $exit_code
