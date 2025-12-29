#!/bin/bash

# Ensures .env file exists by copying from .env.example if needed.
# Exit codes: 0 = success (file exists or was created)

set -e

cd /home/vscode/project

if [ ! -f .env ]; then
    if [ ! -f .env.example ]; then
        echo "[Error] .env.example not found!"
        exit 1
    fi
    echo "[Setup] Creating .env from .env.example..."
    cp .env.example .env
    echo "[Setup] .env created"
else
    echo "[Check] .env exists"
fi
