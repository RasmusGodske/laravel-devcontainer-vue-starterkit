#!/bin/bash
# Shared flock-based queue library for serializing concurrent script runs.
#
# Provides:
#   queue_init "dir" "name"     - Initialize queue directory and variables
#   queue_cleanup_stale         - Remove status files for dead PIDs
#   queue_acquire [options]     - Wait for exclusive lock
#   queue_release --exit-code=N - Release lock and log to history
#   queue_status                - Display current queue state
#
# Usage:
#   source devtools/lib/queue.sh
#   SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
#   queue_init "$SCRIPT_DIR/.php" "test:php"
#   queue_acquire --timeout=600 --command="test:php --parallel"
#   # ... run your command ...
#   queue_release --exit-code=$?

# Module-level variables (set by queue_init)
QUEUE_DIR=""
QUEUE_NAME=""

# Internal variables for duration tracking
_QUEUE_QUEUED_AT=""
_QUEUE_STARTED_AT=""
_QUEUE_COMMAND=""

# ─── queue_init ──────────────────────────────────────────────────────────────
# Initialize the queue directory structure.
#
# Arguments:
#   $1 - Absolute path to the queue directory (e.g., "$SCRIPT_DIR/.php")
#   $2 - Display name for the queue (e.g., "test:php")
#
# Sets:
#   QUEUE_DIR  - Path to the queue directory
#   QUEUE_NAME - Display name for the queue
# ─────────────────────────────────────────────────────────────────────────────
queue_init() {
    local dir="$1"
    local name="$2"

    if [ -z "$dir" ]; then
        echo "ERROR: queue_init requires a directory path as first argument" >&2
        return 1
    fi

    if [ -z "$name" ]; then
        echo "ERROR: queue_init requires a display name as second argument" >&2
        return 1
    fi

    QUEUE_DIR="$dir"
    QUEUE_NAME="$name"

    mkdir -p "$QUEUE_DIR/status"
    touch "$QUEUE_DIR/lock"
}

# ─── queue_cleanup_stale ─────────────────────────────────────────────────────
# Remove status files for PIDs that are no longer alive.
# Called automatically by queue_acquire, but can also be called manually.
# ─────────────────────────────────────────────────────────────────────────────
queue_cleanup_stale() {
    local status_dir="$QUEUE_DIR/status"

    if [ ! -d "$status_dir" ]; then
        return 0
    fi

    for status_file in "$status_dir"/*.json; do
        # Skip if glob didn't match (no .json files)
        [ -f "$status_file" ] || continue

        # Extract PID from filename (e.g., status/12345.json -> 12345)
        local pid
        pid="$(basename "$status_file" .json)"

        # Check if PID is still alive
        if ! kill -0 "$pid" 2>/dev/null; then
            echo "Cleaning stale queue entry for PID $pid"
            rm -f "$status_file"
        fi
    done
}

# ─── _queue_emergency_cleanup ─────────────────────────────────────────────────
# Emergency cleanup on unexpected exit. Removes our status file and closes
# the lock file descriptor.
# ─────────────────────────────────────────────────────────────────────────────
_queue_emergency_cleanup() {
    rm -f "$QUEUE_DIR/status/$$.json" 2>/dev/null
    exec 9>&- 2>/dev/null
}

# ─── queue_acquire ────────────────────────────────────────────────────────────
# Join the queue and wait for exclusive lock.
#
# Options:
#   --timeout=N    Seconds to wait for lock (default: 600). Exit 75 on timeout.
#   --command="…"  Command string for display/logging purposes.
#
# On success: status file updated to "running", FD 9 holds the lock.
# On timeout: status file removed, exits with code 75.
# ─────────────────────────────────────────────────────────────────────────────
queue_acquire() {
    local timeout=600
    local cmd=""

    # Parse arguments
    for arg in "$@"; do
        case "$arg" in
            --timeout=*)
                timeout="${arg#--timeout=}"
                ;;
            --command=*)
                cmd="${arg#--command=}"
                ;;
        esac
    done

    _QUEUE_COMMAND="$cmd"

    # Clean up stale status files from dead processes
    queue_cleanup_stale

    # Record queued timestamp
    local queued_at_iso
    queued_at_iso="$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
    _QUEUE_QUEUED_AT="$(date +%s)"

    # Write status file: state=waiting
    jq -n \
        --argjson pid "$$" \
        --arg state "waiting" \
        --arg command "$cmd" \
        --arg queued_at "$queued_at_iso" \
        '{pid: $pid, state: $state, command: $command, queued_at: $queued_at, lock_acquired_at: null}' \
        > "$QUEUE_DIR/status/$$.json"

    # Open file descriptor 9 on the lock file
    exec 9>"$QUEUE_DIR/lock"

    # Try non-blocking lock first to avoid printing "Waiting..." unnecessarily
    if ! flock --nonblock 9 2>/dev/null; then
        echo "Waiting for $QUEUE_NAME queue..."
        queue_status

        # Blocking lock with timeout
        local flock_exit=0
        flock --exclusive --timeout="$timeout" --conflict-exit-code=75 9 || flock_exit=$?

        if [ "$flock_exit" -ne 0 ]; then
            # Clean up on timeout or failure
            rm -f "$QUEUE_DIR/status/$$.json"
            exec 9>&- 2>/dev/null

            if [ "$flock_exit" -eq 75 ]; then
                echo ""
                echo "ERROR: Timed out after ${timeout}s waiting for $QUEUE_NAME queue."
                echo ""
                queue_status
                exit 75
            else
                echo "ERROR: Failed to acquire $QUEUE_NAME queue lock (exit code: $flock_exit)." >&2
                exit "$flock_exit"
            fi
        fi
    fi

    # Lock acquired - update status file
    local lock_acquired_at_iso
    lock_acquired_at_iso="$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
    _QUEUE_STARTED_AT="$(date +%s)"

    jq -n \
        --argjson pid "$$" \
        --arg state "running" \
        --arg command "$cmd" \
        --arg queued_at "$queued_at_iso" \
        --arg lock_acquired_at "$lock_acquired_at_iso" \
        '{pid: $pid, state: $state, command: $command, queued_at: $queued_at, lock_acquired_at: $lock_acquired_at}' \
        > "$QUEUE_DIR/status/$$.json"

    # Set up emergency cleanup trap, chaining with any existing EXIT trap
    local _existing_trap
    _existing_trap=$(trap -p EXIT | sed "s/trap -- '\(.*\)' EXIT/\1/")
    if [ -n "$_existing_trap" ]; then
        trap "$_existing_trap; _queue_emergency_cleanup" EXIT
    else
        trap '_queue_emergency_cleanup' EXIT
    fi
}

# ─── queue_release ────────────────────────────────────────────────────────────
# Release the lock, log to history, and clean up status file.
#
# Options:
#   --exit-code=N  The exit code of the command that ran (required).
# ─────────────────────────────────────────────────────────────────────────────
queue_release() {
    local exit_code=""

    # Parse arguments
    for arg in "$@"; do
        case "$arg" in
            --exit-code=*)
                exit_code="${arg#--exit-code=}"
                ;;
        esac
    done

    if [ -z "$exit_code" ]; then
        echo "ERROR: queue_release requires --exit-code=N" >&2
        return 1
    fi

    # Record finished timestamp
    local finished_at_iso
    finished_at_iso="$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
    local finished_at_epoch
    finished_at_epoch="$(date +%s)"

    # Calculate durations
    local duration_seconds=0
    local waited_seconds=0

    if [ -n "$_QUEUE_STARTED_AT" ]; then
        duration_seconds=$((finished_at_epoch - _QUEUE_STARTED_AT))
    fi

    if [ -n "$_QUEUE_QUEUED_AT" ] && [ -n "$_QUEUE_STARTED_AT" ]; then
        waited_seconds=$((_QUEUE_STARTED_AT - _QUEUE_QUEUED_AT))
    fi

    # Reconstruct ISO timestamps from what we stored in the status file
    local queued_at_iso=""
    local started_at_iso=""
    if [ -f "$QUEUE_DIR/status/$$.json" ]; then
        queued_at_iso="$(jq -r '.queued_at // ""' "$QUEUE_DIR/status/$$.json")"
        started_at_iso="$(jq -r '.lock_acquired_at // ""' "$QUEUE_DIR/status/$$.json")"
    fi

    # Append history entry
    jq -n -c \
        --argjson pid "$$" \
        --arg command "$_QUEUE_COMMAND" \
        --arg queued_at "$queued_at_iso" \
        --arg started_at "$started_at_iso" \
        --arg finished_at "$finished_at_iso" \
        --argjson duration_seconds "$duration_seconds" \
        --argjson waited_seconds "$waited_seconds" \
        --argjson exit_code "$exit_code" \
        '{pid: $pid, command: $command, queued_at: $queued_at, started_at: $started_at, finished_at: $finished_at, duration_seconds: $duration_seconds, waited_seconds: $waited_seconds, exit_code: $exit_code}' \
        >> "$QUEUE_DIR/history.jsonl"

    # Remove status file
    rm -f "$QUEUE_DIR/status/$$.json"

    # Close FD 9 to release flock
    exec 9>&- 2>/dev/null
}

# ─── queue_status ─────────────────────────────────────────────────────────────
# Display the current state of the queue: running/waiting processes and
# recent history.
# ─────────────────────────────────────────────────────────────────────────────
queue_status() {
    # Clean up stale entries first
    queue_cleanup_stale

    local status_dir="$QUEUE_DIR/status"
    local history_file="$QUEUE_DIR/history.jsonl"
    local has_status=false
    local has_history=false
    local now_epoch
    now_epoch="$(date +%s)"

    # Collect status entries
    local running_entries=()
    local waiting_entries=()

    if [ -d "$status_dir" ]; then
        for status_file in "$status_dir"/*.json; do
            [ -f "$status_file" ] || continue
            has_status=true

            local pid state command queued_at lock_acquired_at
            pid="$(jq -r '.pid' "$status_file")"
            state="$(jq -r '.state' "$status_file")"
            command="$(jq -r '.command' "$status_file")"
            queued_at="$(jq -r '.queued_at' "$status_file")"
            lock_acquired_at="$(jq -r '.lock_acquired_at // ""' "$status_file")"

            local elapsed_label elapsed_seconds

            if [ "$state" = "running" ] && [ -n "$lock_acquired_at" ] && [ "$lock_acquired_at" != "null" ]; then
                # Calculate elapsed since lock acquired
                local started_epoch
                started_epoch="$(date -d "$lock_acquired_at" +%s 2>/dev/null || echo "$now_epoch")"
                elapsed_seconds=$((now_epoch - started_epoch))
                elapsed_label="running $(_queue_format_duration "$elapsed_seconds")"
                running_entries+=("$(printf "  RUNNING:  %-45s (pid %s, %s)" "$command" "$pid" "$elapsed_label")")
            else
                # Calculate elapsed since queued
                local queued_epoch
                queued_epoch="$(date -d "$queued_at" +%s 2>/dev/null || echo "$now_epoch")"
                elapsed_seconds=$((now_epoch - queued_epoch))
                elapsed_label="waiting $(_queue_format_duration "$elapsed_seconds")"
                waiting_entries+=("$(printf "  WAITING:  %-45s (pid %s, %s)" "$command" "$pid" "$elapsed_label")")
            fi
        done
    fi

    # Print status
    if [ "$has_status" = true ]; then
        echo "$QUEUE_NAME queue:"
        # Print running entries first
        for entry in "${running_entries[@]}"; do
            echo "$entry"
        done
        # Then waiting entries
        for entry in "${waiting_entries[@]}"; do
            echo "$entry"
        done
        echo ""
    fi

    # Print recent history
    if [ -f "$history_file" ] && [ -s "$history_file" ]; then
        has_history=true
        echo "Recent history (last 5 runs):"
        tail -n 5 "$history_file" | while IFS= read -r line; do
            local h_finished_at h_exit_code h_duration h_waited h_command h_time h_status_label
            h_finished_at="$(echo "$line" | jq -r '.finished_at // ""')"
            h_exit_code="$(echo "$line" | jq -r '.exit_code')"
            h_duration="$(echo "$line" | jq -r '.duration_seconds')"
            h_waited="$(echo "$line" | jq -r '.waited_seconds')"
            h_command="$(echo "$line" | jq -r '.command')"

            # Extract HH:MM from finished_at
            h_time="$(echo "$h_finished_at" | sed 's/.*T\([0-9][0-9]:[0-9][0-9]\).*/\1/')"

            if [ "$h_exit_code" -eq 0 ] 2>/dev/null; then
                h_status_label="OK  "
            else
                h_status_label="FAIL"
            fi

            printf "  %s %s %4ss (waited %ss)  %s\n" "$h_time" "$h_status_label" "$h_duration" "$h_waited" "$h_command"
        done
    fi

    if [ "$has_status" = false ] && [ "$has_history" = false ]; then
        echo "Queue is empty. No recent runs."
    fi
}

# ─── _queue_format_duration ──────────────────────────────────────────────────
# Format seconds into a human-readable duration string (e.g., "2m13s", "45s").
#
# Arguments:
#   $1 - Duration in seconds
# ─────────────────────────────────────────────────────────────────────────────
_queue_format_duration() {
    local total_seconds="$1"
    local minutes=$((total_seconds / 60))
    local seconds=$((total_seconds % 60))

    if [ "$minutes" -gt 0 ]; then
        echo "${minutes}m${seconds}s"
    else
        echo "${seconds}s"
    fi
}
