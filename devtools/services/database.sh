#!/bin/bash
# PostgreSQL database service
#
# Usage:
#   ./database.sh start [--attach]   Start PostgreSQL
#   ./database.sh stop               Stop PostgreSQL
#   ./database.sh restart [--attach] Restart PostgreSQL
#   ./database.sh status             Check if running
#   ./database.sh logs [N] [--watch] Show logs

# Service configuration
SERVICE_NAME="dev-database"
READY_PATTERN="ready to accept connections"
SERVICE_CMD="cd /home/vscode/project && docker compose up pgsql"

# Source the shared library (resolve symlinks)
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
source "$SCRIPT_DIR/_lib.sh"

# Override do_stop to use docker compose stop
do_stop() {
    echo "[$SERVICE_NAME] Stopping..."

    # Stop the container gracefully
    (cd "$PROJECT_ROOT" && docker compose stop pgsql 2>/dev/null) || true

    # Kill the tmux session if it exists
    if session_exists; then
        tmux kill-session -t "$SERVICE_NAME" 2>/dev/null || true
    fi

    echo "[$SERVICE_NAME] Stopped"
}

# Override do_start to handle already-running containers
do_start() {
    local attach=false
    if [[ "$1" == "--attach" ]]; then
        attach=true
    fi

    if session_healthy; then
        echo "[$SERVICE_NAME] Already running"
        if [[ "$attach" == true ]]; then
            sleep 0.5
            tmux attach-session -t "$SERVICE_NAME"
        fi
        return 0
    fi

    # Kill zombie session if exists
    if session_exists; then
        echo "[$SERVICE_NAME] Cleaning up stale session..."
        tmux kill-session -t "$SERVICE_NAME" 2>/dev/null || true
    fi

    # Check if container is already running
    local is_running
    is_running=$(cd "$PROJECT_ROOT" && docker compose ps --status running pgsql -q 2>/dev/null)

    if [[ -n "$is_running" ]]; then
        echo "[$SERVICE_NAME] Container already running, creating session..."
        tmux new-session -d -s "$SERVICE_NAME" -c "$PROJECT_ROOT" "docker compose logs -f pgsql"
        echo "[$SERVICE_NAME] Ready"
        if [[ "$attach" == true ]]; then
            sleep 0.5
            tmux attach-session -t "$SERVICE_NAME"
        fi
        return 0
    fi

    echo "[$SERVICE_NAME] Starting..."

    # Start in tmux session
    tmux new-session -d -s "$SERVICE_NAME" -c "$PROJECT_ROOT" "$SERVICE_CMD"

    # Wait for container to be running
    local timeout=30
    local elapsed=0

    while [[ $elapsed -lt $timeout ]]; do
        sleep 1
        is_running=$(cd "$PROJECT_ROOT" && docker compose ps --status running pgsql -q 2>/dev/null)

        if [[ -n "$is_running" ]]; then
            echo "[$SERVICE_NAME] Ready"
            if [[ "$attach" == true ]]; then
                sleep 0.5
                tmux attach-session -t "$SERVICE_NAME"
            fi
            return 0
        fi

        ((elapsed++)) || true
    done

    echo "[$SERVICE_NAME] Started (timeout waiting for container)"
    if [[ "$attach" == true ]]; then
        sleep 0.5
        tmux attach-session -t "$SERVICE_NAME"
    fi
    return 0
}

# Override do_status to check docker directly
do_status() {
    local is_running
    is_running=$(cd "$PROJECT_ROOT" && docker compose ps --status running pgsql -q 2>/dev/null)

    if [[ -n "$is_running" ]]; then
        if session_exists; then
            echo "[$SERVICE_NAME] Running (tmux session active)"
        else
            echo "[$SERVICE_NAME] Running (container up, no tmux session)"
        fi
        return 0
    else
        echo "[$SERVICE_NAME] Stopped"
        return 1
    fi
}

# Run the command
run_service_command "$@"
