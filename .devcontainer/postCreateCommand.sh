#!/bin/bash

# Ensure the script fails on any error
set -e

cd /home/vscode/project

# Initialize and update git submodules
git submodule update --init --recursive

# Ensure correct ownership of key directories
sudo chown -R vscode:vscode /home/vscode/project/vendor
sudo chown -R vscode:vscode /home/vscode/project/node_modules

# Install PHP dependencies
if [ -f /home/vscode/project/composer.json ]; then
  echo "Composer.json found, running composer install..."
  composer install
else
  echo "No composer.json found, skipping composer install."
fi

# Install Node dependencies
if [ -f /home/vscode/project/package.json ]; then
  echo "Package.json found, running npm install..."
  npm install

  # Install Playwright browsers if @playwright/test is a dependency
  if grep -q "@playwright/test" /home/vscode/project/package.json; then
    echo "Playwright found, installing browsers..."
    npx playwright install chromium
  fi
else
  echo "No package.json found, skipping npm install."
fi

# Generate app key if not set (initializeCommand already copied .env)
if grep -q "^APP_KEY=$" /home/vscode/project/.env 2>/dev/null; then
  echo "Generating application key..."
  php artisan key:generate
fi

