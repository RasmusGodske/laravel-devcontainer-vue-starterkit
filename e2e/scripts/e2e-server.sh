#!/bin/bash

# E2E Test Server Startup Script
# This script starts the Laravel server for E2E testing with isolated configuration

set -e

# Configuration
PORT=${E2E_PORT:-8081}
HOST=${E2E_HOST:-127.0.0.1}
ENV_FILE=".env.e2e"
PID_FILE="/tmp/e2e-server.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[E2E]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[E2E]${NC} $1"
}

print_error() {
    echo -e "${RED}[E2E]${NC} $1"
}

# Function to stop the server
stop_server() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            print_info "Stopping E2E server (PID: $PID)..."
            kill "$PID" 2>/dev/null || true
            sleep 1
            # Force kill if still running
            if kill -0 "$PID" 2>/dev/null; then
                kill -9 "$PID" 2>/dev/null || true
            fi
            print_info "Server stopped"
        fi
        rm -f "$PID_FILE"
    fi
}

# Function to start the server
start_server() {
    print_info "Starting E2E test server..."

    # Check if env file exists
    if [ ! -f "$ENV_FILE" ]; then
        print_error "E2E environment file not found: $ENV_FILE"
        print_info "Creating from .env.example..."
        cp .env.example "$ENV_FILE"
        print_warning "Please configure $ENV_FILE for E2E testing"
    fi

    # Generate app key if needed
    if grep -q "APP_KEY=$" "$ENV_FILE" || grep -q "APP_KEY=base64:e2etestingkey" "$ENV_FILE"; then
        print_info "Generating application key..."
        php artisan key:generate --env=e2e --force
    fi

    # Run migrations
    print_info "Running database migrations..."
    php artisan migrate:fresh --env=e2e --force --seed 2>/dev/null || php artisan migrate:fresh --env=e2e --force

    # Stop any existing server
    stop_server

    # Start the server in background
    print_info "Starting server on $HOST:$PORT..."
    php artisan serve --env=e2e --host="$HOST" --port="$PORT" &
    echo $! > "$PID_FILE"

    # Wait for server to be ready
    print_info "Waiting for server to be ready..."
    for i in {1..30}; do
        if curl -s "http://$HOST:$PORT" > /dev/null 2>&1; then
            print_info "Server is ready at http://$HOST:$PORT"
            return 0
        fi
        sleep 1
    done

    print_error "Server failed to start within 30 seconds"
    stop_server
    return 1
}

# Handle script arguments
case "${1:-start}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        stop_server
        start_server
        ;;
    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                print_info "Server is running (PID: $PID)"
            else
                print_warning "PID file exists but server is not running"
                rm -f "$PID_FILE"
            fi
        else
            print_info "Server is not running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
