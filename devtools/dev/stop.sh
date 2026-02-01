#!/bin/bash
# Stop the development environment
#
# Usage:
#   ./stop.sh           Stop all services
#   ./stop.sh --all     Stop all services including Docker

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
SERVICES_DIR="$(dirname "$SCRIPT_DIR")/services"

include_infra=false
if [[ "$1" == "--all" ]]; then
    include_infra=true
fi

echo "=== Stopping Development Environment ==="
echo ""

echo "Stopping Vite..."
"$SERVICES_DIR/vite.sh" stop

echo ""
echo "Stopping Laravel server..."
"$SERVICES_DIR/serve.sh" stop

echo ""
echo "Stopping logs..."
"$SERVICES_DIR/logs.sh" stop

if [[ "$include_infra" == true ]]; then
    echo ""
    echo "Stopping cache..."
    "$SERVICES_DIR/cache.sh" stop

    echo ""
    echo "Stopping database..."
    "$SERVICES_DIR/database.sh" stop
else
    echo ""
    echo "(Database and cache left running - use --all to stop them too)"
fi

echo ""
echo "=== Development Environment Stopped ==="
