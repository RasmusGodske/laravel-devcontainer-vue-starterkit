#!/bin/bash

# Get the project name from the directory name
PROJECT_NAME=$(basename "$PWD")

echo ""
echo "=========================================="
echo "Setup complete! "
# Guide developer to use tasks `Dev: Start` to get started
echo "To get started, use the VS Code command palette (Ctrl+Shift+P) and run the task 'Dev: Start'."
echo ""
echo "  - 'Dev: Start' to launch all necessary services and processes."
echo "  - 'Composer: dump-autoload' to refresh the Composer autoloader."
echo "  - 'Artisan: optimize:clear' to clear all caches."
echo "  - 'Database: migrate:fresh --seed' to reset and seed the database."
echo ""

# Guide to common commands to run the application
echo "You can now run:"
echo ""
echo "  - docker compose up"
echo "  - php artisan serve --host=0.0.0.0 --port=8080"
echo "  - npm run dev"
echo "  - php artisan migrate:fresh --seed"
echo "  - php artisan pail --timeout=0"
echo ""
echo "=========================================="
