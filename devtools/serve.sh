#!/bin/bash
# Wrapper script for php artisan serve that handles restarts gracefully
# Reads APP_PORT from .env (set by devtools/setup/configure-access.sh)

cd /home/vscode/project

# Read APP_PORT from .env, fallback to 8080
read_app_port() {
    grep '^APP_PORT=' .env 2>/dev/null | cut -d= -f2 | head -1
}

PORT="${1:-$(read_app_port)}"
PORT="${PORT:-8080}"
HOST="${2:-0.0.0.0}"

kill_port() {
    if command -v fuser &> /dev/null; then
        fuser -k "$PORT/tcp" 2>/dev/null
    elif command -v lsof &> /dev/null; then
        lsof -ti:"$PORT" | xargs -r kill -9 2>/dev/null
    fi
    sleep 0.5
}

# Handle SIGTERM/SIGINT gracefully
trap 'kill_port; exit 0' SIGTERM SIGINT

# Loop to handle restarts (e.g., when .env changes trigger reload)
while true; do
    kill_port
    php artisan serve --host="$HOST" --port="$PORT"
    EXIT_CODE=$?

    # If server exited cleanly (manual stop), don't restart
    if [ $EXIT_CODE -eq 0 ]; then
        break
    fi

    echo "Server exited with code $EXIT_CODE, restarting in 1 second..."
    sleep 1
done
