#!/bin/bash
# Run TypeScript type checking
#
# This script runs vue-tsc to check for TypeScript type errors.
# For ESLint code quality checks, use lint:js instead.
#
# Usage:
#   ./devtools/lint/ts.sh                              # Type-check all files
#   ./devtools/lint/ts.sh resources/js/Pages/Login.vue # Type-check specific file
#   ./devtools/lint/ts.sh resources/js/Pages/*.vue     # Type-check multiple files
#
# Alias: lint:ts (via symlink in /usr/local/bin)
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
            echo "Usage: lint:ts [OPTIONS] [FILES...]"
            echo ""
            echo "Run TypeScript type checking"
            echo ""
            echo "Options:"
            echo "  --no-lumby     Skip AI diagnosis on failure"
            echo "  --help, -h     Show this help message"
            echo ""
            echo "Examples:"
            echo "  lint:ts                                # Type-check all files"
            echo "  lint:ts resources/js/Pages/Login.vue   # Type-check specific file"
            echo "  lint:ts resources/js/Pages/*.vue       # Type-check multiple files"
            echo ""
            echo "For ESLint code quality checks, use: lint:js"
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

if [ ${#FILES[@]} -eq 0 ]; then
    # No files specified - type-check everything
    echo "=== Running TypeScript type-check ==="
    run_cmd npm run type-check
else
    # Files specified - type-check only those files
    echo "=== Running TypeScript type-check on specified files ==="
    printf '  %s\n' "${FILES[@]}"
    echo ""
    run_cmd npm run type-check:files -- "${FILES[@]}"
fi

echo ""
echo "TypeScript: PASSED"
