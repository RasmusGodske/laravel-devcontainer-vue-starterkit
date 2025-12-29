#!/bin/bash

# Ensures composer dependencies are installed.
# Runs composer install if vendor directory is missing or composer.lock changed.
# Exit codes: 0 = success

set -e

cd /home/vscode/project

if [ ! -f composer.lock ]; then
    echo "[Error] composer.lock not found!"
    exit 1
fi

if [ ! -d vendor ]; then
    echo "[Setup] Installing composer dependencies..."
    composer install --no-interaction
    echo "[Setup] Composer dependencies installed"
elif [ composer.lock -nt vendor ]; then
    echo "[Setup] composer.lock changed, updating dependencies..."
    composer install --no-interaction
    echo "[Setup] Composer dependencies updated"
else
    echo "[Check] Composer dependencies are up to date"
fi
