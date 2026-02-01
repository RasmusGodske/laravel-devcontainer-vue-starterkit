#!/bin/bash
# Shared library for tmux-managed development services
#
# Usage: Source this file and call the functions
#   source "$(dirname "$0")/_lib.sh"
#
# Each service script should define:
#   SERVICE_NAME    - tmux session name (e.g., "dev-serve")
#   SERVICE_CMD     - command to run (e.g., "php artisan serve")
#   READY_PATTERN   - pattern that indicates service is ready (for VS Code task matching)

# Note: We don't use 'set -e' here because grep returns 1 when no match,
# which would cause premature exit in our pattern detection loops.

PROJECT_ROOT="/home/vscode/project"

# Check if a tmux session exists
session_exists() {
    tmux has-session -t "$SERVICE_NAME" 2>/dev/null
}

# Check if the process inside the session is still running
# Returns 0 if running, 1 if session exists but process died
session_healthy() {
    if ! session_exists; then
        return 1
    fi

    # Check if there's an active process (not just a dead shell)
    # tmux list-panes shows if the pane is still active
    local pane_pid
    pane_pid=$(tmux list-panes -t "$SERVICE_NAME" -F '#{pane_pid}' 2>/dev/null | head -1)

    if [[ -z "$pane_pid" ]]; then
        return 1
    fi

    # Check if that process has children (the actual service)
    if pgrep -P "$pane_pid" > /dev/null 2>&1; then
        return 0
    fi

    return 1
}

# Start the service in a tmux session
# Usage: do_start [--attach]
do_start() {
    local attach=false
    if [[ "$1" == "--attach" ]]; then
        attach=true
    fi

    local was_running=false
    if session_healthy; then
        was_running=true
        echo "[$SERVICE_NAME] Already running"
        # Output the ready pattern so VS Code task completes
        if [[ -n "$READY_PATTERN" ]]; then
            echo "$READY_PATTERN"
        fi
    else
        # Kill zombie session if exists
        if session_exists; then
            echo "[$SERVICE_NAME] Cleaning up stale session..."
            tmux kill-session -t "$SERVICE_NAME" 2>/dev/null || true
        fi

        echo "[$SERVICE_NAME] Starting..."

        # Start the service in a new tmux session
        tmux new-session -d -s "$SERVICE_NAME" -c "$PROJECT_ROOT" "$SERVICE_CMD"

        # Wait for ready pattern (or timeout)
        local timeout=30
        local elapsed=0
        local output=""

        while [[ $elapsed -lt $timeout ]]; do
            sleep 1
            output=$(tmux capture-pane -t "$SERVICE_NAME" -p 2>/dev/null || echo "")

            if [[ -n "$READY_PATTERN" ]] && echo "$output" | grep -qF "$READY_PATTERN"; then
                # Print the captured output for VS Code pattern matching
                echo "$output"
                echo "[$SERVICE_NAME] Ready"
                break
            fi

            ((elapsed++)) || true
        done

        if [[ $elapsed -ge $timeout ]]; then
            # Timeout - still print output and succeed (service may still be starting)
            echo "$output"
            echo "[$SERVICE_NAME] Started (timeout waiting for ready pattern)"
        fi
    fi

    # Attach if requested
    if [[ "$attach" == true ]]; then
        sleep 0.5
        tmux attach-session -t "$SERVICE_NAME"
    fi

    return 0
}

# Stop the service
do_stop() {
    if ! session_exists; then
        echo "[$SERVICE_NAME] Not running"
        return 0
    fi

    echo "[$SERVICE_NAME] Stopping..."

    # Send SIGTERM to the process
    tmux send-keys -t "$SERVICE_NAME" C-c
    sleep 1

    # Kill the session
    tmux kill-session -t "$SERVICE_NAME" 2>/dev/null || true

    echo "[$SERVICE_NAME] Stopped"
}

# Restart the service
# Usage: do_restart [--attach]
do_restart() {
    local attach=""
    if [[ "$1" == "--attach" ]]; then
        attach="--attach"
    fi

    do_stop
    sleep 1
    do_start $attach
}

# Check status
do_status() {
    if session_healthy; then
        echo "[$SERVICE_NAME] Running"
        return 0
    elif session_exists; then
        echo "[$SERVICE_NAME] Stale (session exists but process died)"
        return 1
    else
        echo "[$SERVICE_NAME] Stopped"
        return 1
    fi
}

# Show recent logs
# Usage: do_logs [N] [--watch]
do_logs() {
    local lines=50
    local watch=false

    # Parse arguments
    for arg in "$@"; do
        case "$arg" in
            --watch|-f)
                watch=true
                ;;
            [0-9]*)
                lines="$arg"
                ;;
        esac
    done

    if ! session_exists; then
        echo "[$SERVICE_NAME] Not running - no logs available"
        return 1
    fi

    if [[ "$watch" == true ]]; then
        echo "=== $SERVICE_NAME logs (watching, Ctrl+C to exit) ==="
        while true; do
            clear
            echo "=== $SERVICE_NAME logs (last $lines lines, watching) ==="
            tmux capture-pane -t "$SERVICE_NAME" -p -S -"$lines"
            sleep 1
        done
    else
        echo "=== $SERVICE_NAME logs (last $lines lines) ==="
        tmux capture-pane -t "$SERVICE_NAME" -p -S -"$lines"
    fi
}

# Attach to the session (interactive)
do_attach() {
    if ! session_exists; then
        echo "[$SERVICE_NAME] Not running"
        return 1
    fi

    echo "Attaching to $SERVICE_NAME (Ctrl+B, D to detach)..."
    tmux attach-session -t "$SERVICE_NAME"
}

# Main command dispatcher
run_service_command() {
    local cmd="${1:-start}"
    shift || true

    case "$cmd" in
        start)
            do_start "$@"
            ;;
        stop)
            do_stop "$@"
            ;;
        restart)
            do_restart "$@"
            ;;
        status)
            do_status "$@"
            ;;
        logs)
            do_logs "$@"
            ;;
        attach)
            do_attach "$@"
            ;;
        *)
            echo "Usage: $0 <command> [options]"
            echo ""
            echo "Commands:"
            echo "  start [--attach]     Start the service (--attach to follow output)"
            echo "  stop                 Stop the service"
            echo "  restart [--attach]   Restart the service"
            echo "  status               Check if service is running"
            echo "  logs [N] [--watch]   Show last N lines (default: 50, --watch to follow)"
            echo "  attach               Attach to tmux session (interactive)"
            exit 1
            ;;
    esac
}
