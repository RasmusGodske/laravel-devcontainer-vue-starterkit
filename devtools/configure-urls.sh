#!/bin/bash
# Configures APP_URL and Vite HMR settings based on environment
# - In local environment: defaults to localhost (no prompt)
# - In Codespaces: prompts user to choose between browser access and port forwarding

set -e

cd "$(dirname "$0")/.."

# Ensure .env exists
if [[ ! -f .env ]]; then
    echo "Error: .env file not found. Run ensure-env.sh first."
    exit 1
fi

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
    echo "✓ Configured for localhost access"
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

    echo "✓ Configured for Codespaces browser access"
    echo "  APP_URL: ${codespace_url}"
    echo "  ASSET_URL: ${vite_dev_server_url}"
}

# If not in Codespaces, default to localhost (no prompt)
if [[ "$CODESPACES" != "true" ]]; then
    echo "Local environment detected"
    configure_localhost
    exit 0
fi

# In Codespaces - prompt for mode
echo ""
echo "🌐 GitHub Codespaces detected!"
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
