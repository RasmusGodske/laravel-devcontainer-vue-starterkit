#!/bin/bash
# Configures APP_URL and Vite HMR settings based on environment
#
# Usage:
#   ./urls.sh              Run setup (direct, for backwards compatibility)
#   ./urls.sh run          Run setup in tmux session (captures output)
#   ./urls.sh run --attach Run setup in tmux and attach to watch
#   ./urls.sh status       Check if URLs are configured
#   ./urls.sh logs [N]     Show setup output from tmux session

SETUP_NAME="setup-urls"
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

cd /home/vscode/project

# Helper function to update or add env var
update_env() {
    local key="$1"
    local value="$2"
    if grep -q "^${key}=" .env; then
        sed -i "s|^${key}=.*|${key}=${value}|" .env
    else
        echo "${key}=${value}" >> .env
    fi
}

# Helper function to remove env var
remove_env() {
    local key="$1"
    sed -i "/^${key}=/d" .env
}

# Configure for localhost (default/port-forwarded mode)
configure_localhost() {
    update_env "APP_URL" "http://localhost"
    remove_env "ASSET_URL"
    remove_env "VITE_DEV_SERVER_URL"
    remove_env "VITE_HMR_HOST"
    remove_env "VITE_HMR_PROTOCOL"
    remove_env "VITE_HMR_CLIENT_PORT"
    echo "[Setup] Configured for localhost access"
}

# Configure for Codespaces browser access
configure_codespaces_browser() {
    local app_port="${APP_PORT:-8080}"
    local codespace_url="https://${CODESPACE_NAME}-${app_port}.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    local vite_host="${CODESPACE_NAME}-5173.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    local vite_dev_server_url="https://${vite_host}"

    update_env "APP_URL" "${codespace_url}"
    update_env "ASSET_URL" "${vite_dev_server_url}"
    update_env "VITE_DEV_SERVER_URL" "${vite_dev_server_url}"
    update_env "VITE_HMR_HOST" "${vite_host}"
    update_env "VITE_HMR_PROTOCOL" "wss"
    update_env "VITE_HMR_CLIENT_PORT" "443"

    echo "[Setup] Configured for Codespaces browser access"
    echo "  APP_URL: ${codespace_url}"
    echo "  VITE_DEV_SERVER_URL: ${vite_dev_server_url}"
}

# The actual setup logic
do_setup() {
    # Ensure .env exists
    if [[ ! -f .env ]]; then
        echo "[Error] .env file not found. Run env.sh first."
        return 1
    fi

    # If not in Codespaces, default to localhost (no prompt)
    if [[ "$CODESPACES" != "true" ]]; then
        echo "[Check] Local environment detected"
        configure_localhost
        return 0
    fi

    # In Codespaces - prompt for mode
    echo ""
    echo "GitHub Codespaces detected!"
    echo ""
    echo "How are you accessing this environment?"
    echo "  1) Browser (app.github.dev URL)"
    echo "  2) VS Code Desktop with port forwarding (localhost)"
    echo ""
    read -p "Select [1/2]: " choice

    case $choice in
        1)
            configure_codespaces_browser
            ;;
        2|*)
            configure_localhost
            ;;
    esac
}

# Status check (quick, no setup)
do_status() {
    if grep -q "^APP_URL=" .env 2>/dev/null; then
        local app_url
        app_url=$(grep "^APP_URL=" .env | cut -d= -f2)
        echo "[ok] APP_URL is set ($app_url)"
        return 0
    else
        echo "[missing] APP_URL not configured"
        return 1
    fi
}

# Source shared library for tmux functions
source "$SCRIPT_DIR/_lib.sh"

# Command dispatcher
case "${1:-}" in
    run)
        shift
        run_setup_in_tmux "$@"
        ;;
    status)
        do_status
        ;;
    logs)
        show_setup_logs "${2:-50}"
        ;;
    *)
        # Backwards compatible - run directly
        do_setup
        ;;
esac
