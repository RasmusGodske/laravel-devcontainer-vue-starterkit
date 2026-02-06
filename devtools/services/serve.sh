#!/bin/bash
# Laravel development server service
#
# Watches APP_PORT in .env and auto-restarts when it changes.
#
# Usage:
#   ./serve.sh start      Start the server (or report if already running)
#   ./serve.sh stop       Stop the server
#   ./serve.sh restart    Restart the server
#   ./serve.sh status     Check if running
#   ./serve.sh logs [N]   Show last N lines of output
#   ./serve.sh attach     Attach to tmux session

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

# ---------------------------------------------------------------------------
# Watched runner mode (runs INSIDE the tmux session)
# ---------------------------------------------------------------------------
if [[ "${1:-}" == "--run-watched" ]]; then
    source "$SCRIPT_DIR/_env-watch.sh"

    CURRENT_PORT=""

    build_serve_cmd() {
        local port host
        port=$(read_env_value "APP_PORT")
        port="${port:-8080}"
        host="${SERVE_HOST:-0.0.0.0}"
        CURRENT_PORT="$port"
        CMD_TO_RUN="fuser -k $port/tcp 2>/dev/null; sleep 0.5; exec php artisan serve --host=$host --port=$port"
    }

    cleanup_serve() {
        [[ -n "$CURRENT_PORT" ]] && fuser -k "$CURRENT_PORT/tcp" 2>/dev/null || true
    }

    run_with_env_watch 3 "APP_PORT" build_serve_cmd cleanup_serve
    exit $?
fi

# ---------------------------------------------------------------------------
# Normal service management mode
# ---------------------------------------------------------------------------

SERVICE_NAME="dev-serve"
READY_PATTERN="Server running on"

# Read port for do_stop (fresh read each invocation)
PORT="${SERVE_PORT:-${APP_PORT:-$(grep '^APP_PORT=' /home/vscode/project/.env 2>/dev/null | cut -d= -f2)}}"
PORT="${PORT:-8080}"

SERVICE_CMD="cd /home/vscode/project && $SCRIPT_DIR/serve.sh --run-watched"

# Source the shared library (resolve symlinks)
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
