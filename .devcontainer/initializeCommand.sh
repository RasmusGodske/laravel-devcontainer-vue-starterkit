#!/bin/bash

# Create .env from .env.example if it doesn't exist (needed for docker compose)
if [ ! -f .env ] && [ -f .env.example ]; then
    cp .env.example .env
fi
