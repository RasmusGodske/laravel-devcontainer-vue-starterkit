#!/bin/bash
# Run all project checks (ESLint, PHPStan, PHP tests)
#
# This script runs all quality checks in sequence and reports results.
# It's designed to be used by developers for a complete project check,
# or by CI/CD pipelines for automated validation.
#
# Usage:
#   ./devtools/qa.sh                        # Run all checks
#   ./devtools/qa.sh --output-file=result.txt  # Save results to file
#   ./devtools/qa.sh --output-dir=/tmp     # Save results to directory
#   ./devtools/qa.sh --exit-on-failure     # Stop on first failure
#   ./devtools/qa.sh --skip-eslint         # Skip ESLint
#   ./devtools/qa.sh --skip-php-tests      # Skip PHP tests
#   ./devtools/qa.sh --skip-phpstan        # Skip PHPStan
#
# Alias: qa (via symlink in /usr/local/bin)
#
# Exit codes:
#   0 - All checks passed
#   1 - One or more checks failed

set -o pipefail

# Resolve symlinks to get actual script location
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Default values
OUTPUT_FILE=""
OUTPUT_DIR=""
EXIT_ON_FAILURE=false
SKIP_PHP_TESTS=false
SKIP_PHPSTAN=false
SKIP_ESLINT=false
QUIET=false

# Colors for output (only if terminal supports it)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    BOLD=''
    NC=''
fi

# Parse arguments
for arg in "$@"; do
    case $arg in
        --output-file=*)
            OUTPUT_FILE="${arg#*=}"
            shift
            ;;
        --output-dir=*)
            OUTPUT_DIR="${arg#*=}"
            shift
            ;;
        --exit-on-failure)
            EXIT_ON_FAILURE=true
            shift
            ;;
        --skip-php-tests)
            SKIP_PHP_TESTS=true
            shift
            ;;
        --skip-phpstan)
            SKIP_PHPSTAN=true
            shift
            ;;
        --skip-eslint)
            SKIP_ESLINT=true
            shift
            ;;
        --quiet|-q)
            QUIET=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Run all project checks (ESLint, PHPStan, PHP tests)"
            echo ""
            echo "Options:"
            echo "  --output-file=FILE    Save results summary to FILE"
            echo "  --output-dir=DIR      Save results to directory DIR"
            echo "  --exit-on-failure     Stop on first check failure"
            echo "  --skip-eslint         Skip ESLint"
            echo "  --skip-php-tests      Skip PHP tests"
            echo "  --skip-phpstan        Skip PHPStan analysis"
            echo "  --quiet, -q           Suppress verbose output"
            echo "  --help, -h            Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Resolve output file path
if [ -n "$OUTPUT_DIR" ] && [ -z "$OUTPUT_FILE" ]; then
    OUTPUT_FILE="$OUTPUT_DIR/check-results.txt"
fi

# Track results
declare -A CHECK_RESULTS
declare -A CHECK_DURATIONS
declare -A CHECK_OUTPUTS
CHECKS_RUN=0
CHECKS_PASSED=0
CHECKS_FAILED=0
START_TIME=$(date +%s)

# Logging functions
log() {
    if [ "$QUIET" != "true" ]; then
        echo -e "$@"
    fi
}

log_header() {
    log ""
    log "${BLUE}${BOLD}════════════════════════════════════════════════════════════════${NC}"
    log "${BLUE}${BOLD}  $1${NC}"
    log "${BLUE}${BOLD}════════════════════════════════════════════════════════════════${NC}"
}

log_result() {
    local check_name=$1
    local status=$2
    local duration=$3

    if [ "$status" = "passed" ]; then
        log "${GREEN}✓${NC} $check_name ${GREEN}PASSED${NC} (${duration}s)"
    elif [ "$status" = "failed" ]; then
        log "${RED}✗${NC} $check_name ${RED}FAILED${NC} (${duration}s)"
    else
        log "${YELLOW}○${NC} $check_name ${YELLOW}SKIPPED${NC}"
    fi
}

# Run a check and capture results
run_check() {
    local check_name=$1
    local check_script=$2
    shift 2
    local check_args=("$@")

    log_header "Running $check_name"

    local check_start=$(date +%s)
    local output_file=$(mktemp)

    # Run the check - stream output in real-time while capturing for summary
    local exit_code
    if [ "$QUIET" != "true" ]; then
        # Stream to terminal AND capture to file
        "$check_script" "${check_args[@]}" 2>&1 | tee "$output_file"
        exit_code=${PIPESTATUS[0]}  # Get exit code of check script, not tee
    else
        # Quiet mode - capture only, no streaming
        "$check_script" "${check_args[@]}" > "$output_file" 2>&1
        exit_code=$?
    fi

    if [ "$exit_code" -eq 0 ]; then
        local status="passed"
        ((CHECKS_PASSED++))
    else
        local status="failed"
        ((CHECKS_FAILED++))
    fi

    local check_end=$(date +%s)
    local duration=$((check_end - check_start))

    # Store results
    CHECK_RESULTS[$check_name]=$status
    CHECK_DURATIONS[$check_name]=$duration
    CHECK_OUTPUTS[$check_name]=$(cat "$output_file")
    ((CHECKS_RUN++))

    rm -f "$output_file"

    log ""
    log_result "$check_name" "$status" "$duration"

    # Exit early if requested
    if [ "$EXIT_ON_FAILURE" = "true" ] && [ "$status" = "failed" ]; then
        log ""
        log "${RED}${BOLD}Stopping due to --exit-on-failure${NC}"
        print_summary
        exit 1
    fi

    return 0
}

# Print summary
print_summary() {
    local end_time=$(date +%s)
    local total_duration=$((end_time - START_TIME))

    local summary=""
    summary+="
================================================================================
                           CHECK RESULTS SUMMARY
================================================================================

"

    # Individual results
    for check_name in "ESLint" "PHPStan" "PHP Tests"; do
        if [ -n "${CHECK_RESULTS[$check_name]}" ]; then
            local status="${CHECK_RESULTS[$check_name]}"
            local duration="${CHECK_DURATIONS[$check_name]}"
            if [ "$status" = "passed" ]; then
                summary+="  [PASS] $check_name (${duration}s)
"
            else
                summary+="  [FAIL] $check_name (${duration}s)
"
            fi
        elif [ "$check_name" = "ESLint" ] && [ "$SKIP_ESLINT" = "true" ]; then
            summary+="  [SKIP] $check_name
"
        elif [ "$check_name" = "PHPStan" ] && [ "$SKIP_PHPSTAN" = "true" ]; then
            summary+="  [SKIP] $check_name
"
        elif [ "$check_name" = "PHP Tests" ] && [ "$SKIP_PHP_TESTS" = "true" ]; then
            summary+="  [SKIP] $check_name
"
        fi
    done

    summary+="
--------------------------------------------------------------------------------
"

    if [ "$CHECKS_FAILED" -eq 0 ] && [ "$CHECKS_RUN" -gt 0 ]; then
        summary+="  Result: ALL CHECKS PASSED ($CHECKS_PASSED/$CHECKS_RUN)
"
    elif [ "$CHECKS_RUN" -eq 0 ]; then
        summary+="  Result: NO CHECKS RUN (all skipped)
"
    else
        summary+="  Result: CHECKS FAILED ($CHECKS_FAILED/$CHECKS_RUN failed)
"
    fi

    summary+="  Total time: ${total_duration}s

================================================================================
"

    echo -e "$summary"

    # Write to output file if specified
    if [ -n "$OUTPUT_FILE" ]; then
        # Ensure directory exists
        mkdir -p "$(dirname "$OUTPUT_FILE")"

        # Write summary
        echo "$summary" > "$OUTPUT_FILE"

        # Append failure details if any
        if [ "$CHECKS_FAILED" -gt 0 ]; then
            echo "" >> "$OUTPUT_FILE"
            echo "FAILURE DETAILS:" >> "$OUTPUT_FILE"
            echo "================" >> "$OUTPUT_FILE"
            for check_name in "ESLint" "PHPStan" "PHP Tests"; do
                if [ "${CHECK_RESULTS[$check_name]}" = "failed" ]; then
                    echo "" >> "$OUTPUT_FILE"
                    echo "--- $check_name Output ---" >> "$OUTPUT_FILE"
                    echo "${CHECK_OUTPUTS[$check_name]}" >> "$OUTPUT_FILE"
                fi
            done
        fi

        log "Results saved to: $OUTPUT_FILE"
    fi
}

# Main execution
cd "$PROJECT_DIR"

log "${BOLD}Starting all project checks...${NC}"
log "Project: $PROJECT_DIR"
log "Time: $(date)"
log ""

# Run ESLint first (fastest, catches frontend code quality issues)
if [ "$SKIP_ESLINT" != "true" ]; then
    run_check "ESLint" "$SCRIPT_DIR/lint/js.sh"
else
    log "${YELLOW}Skipping ESLint (--skip-eslint)${NC}"
fi

# Run PHPStan (fast, catches PHP type errors)
if [ "$SKIP_PHPSTAN" != "true" ]; then
    run_check "PHPStan" "$SCRIPT_DIR/lint/php.sh"
else
    log "${YELLOW}Skipping PHPStan (--skip-phpstan)${NC}"
fi

# Run PHP Tests (medium speed, tests backend logic)
if [ "$SKIP_PHP_TESTS" != "true" ]; then
    run_check "PHP Tests" "$SCRIPT_DIR/test/php.sh" --parallel
else
    log "${YELLOW}Skipping PHP Tests (--skip-php-tests)${NC}"
fi

# Print summary
print_summary

# Exit with appropriate code
if [ "$CHECKS_FAILED" -gt 0 ]; then
    exit 1
else
    exit 0
fi
