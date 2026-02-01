#!/bin/bash
# Laravel development server service
#
# Usage:
#   ./serve.sh start      Start the server (or report if already running)
#   ./serve.sh stop       Stop the server
#   ./serve.sh restart    Restart the server
#   ./serve.sh status     Check if running
#   ./serve.sh logs [N]   Show last N lines of output
#   ./serve.sh attach     Attach to tmux session

# Service configuration
SERVICE_NAME="dev-serve"
READY_PATTERN="Server running on"

PORT="${SERVE_PORT:-8080}"
HOST="${SERVE_HOST:-0.0.0.0}"

# The command includes port cleanup and the artisan serve
SERVICE_CMD="cd /home/vscode/project && fuser -k $PORT/tcp 2>/dev/null; sleep 0.5; php artisan serve --host=$HOST --port=$PORT"

# Source the shared library (resolve symlinks)
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
source "$SCRIPT_DIR/_lib.sh"

# Override do_stop to clean up the port
do_stop() {
    if ! session_exists; then
        echo "[$SERVICE_NAME] Not running"
        # Still try to free the port in case something else is using it
        fuser -k "$PORT/tcp" 2>/dev/null || true
        return 0
    fi

    echo "[$SERVICE_NAME] Stopping..."

    # Send SIGTERM to the process
    tmux send-keys -t "$SERVICE_NAME" C-c
    sleep 1

    # Kill the session
    tmux kill-session -t "$SERVICE_NAME" 2>/dev/null || true

    # Make sure port is freed
    fuser -k "$PORT/tcp" 2>/dev/null || true

    echo "[$SERVICE_NAME] Stopped"
}

# Run the command
run_service_command "$@"
