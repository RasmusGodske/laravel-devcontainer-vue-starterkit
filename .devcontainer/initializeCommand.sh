#!/bin/bash

# Get the project name from the directory name
PROJECT_NAME=$(basename "$PWD")

# Create .env from .env.example if it doesn't exist (needed for docker compose)
if [ ! -f .env ] && [ -f .env.example ]; then
    cp .env.example .env
fi

# Create the network if it doesn't exist
docker network create "${PROJECT_NAME}_app-network" 2>/dev/null || true
