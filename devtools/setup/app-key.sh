#!/bin/bash

# Ensures APP_KEY is set in .env by generating one if needed.
# Exit codes: 0 = success (key exists or was generated)

set -e

cd /home/vscode/project

if [ ! -f .env ]; then
    echo "[Error] .env file not found! Run ensure-env.sh first."
    exit 1
fi

if grep -q "^APP_KEY=base64:" .env 2>/dev/null; then
    echo "[Check] APP_KEY is set"
else
    echo "[Setup] Generating application key..."
    php artisan key:generate
    echo "[Setup] Application key generated"
fi
