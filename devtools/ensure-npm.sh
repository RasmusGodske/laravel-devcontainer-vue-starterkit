#!/bin/bash

# Ensures npm dependencies are installed.
# Runs npm install if node_modules directory is missing or package-lock.json changed.
# Exit codes: 0 = success

set -e

cd /home/vscode/project

if [ ! -f package-lock.json ]; then
    echo "[Error] package-lock.json not found!"
    exit 1
fi

if [ ! -d node_modules ]; then
    echo "[Setup] Installing npm dependencies..."
    npm install
    echo "[Setup] npm dependencies installed"
elif [ package-lock.json -nt node_modules ]; then
    echo "[Setup] package-lock.json changed, updating dependencies..."
    npm install
    echo "[Setup] npm dependencies updated"
else
    echo "[Check] npm dependencies are up to date"
fi
