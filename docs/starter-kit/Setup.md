# Setup Guide

This guide provides step-by-step instructions for recreating this Laravel starter kit. Each step is documented in detail to explain why it's necessary and how to implement it.

## Overview

This Laravel starter kit includes:
- **Vue 3** with Inertia.js for modern frontend development
- **VS Code Dev Containers** for a consistent development environment (no Laravel Sail)
- **TypeScript** integration with automatic type generation
- **Code quality tools** including Pint formatting and Git hooks
- **IDE enhancements** for better developer experience
- **PostgreSQL** and **Redis** for database and caching
- **E2E Testing** with Playwright for browser automation
- **Claude Code Rules** for AI-assisted development with consistent conventions
- **Devtools** for environment setup and AI code review hooks

## Why No Laravel Sail?

This starter kit runs PHP directly in the VS Code devcontainer instead of using Laravel Sail. This provides:
- Faster command execution (no wrapper overhead)
- Better IDE integration (PHP runs where your extensions run)
- Simpler debugging (Xdebug in same container as IDE)
- Lower resource usage (one fewer container)

## Setup Steps

Follow these steps in order to recreate the starter kit:

1. **[Laravel Installation](01-laravel-installation.md)** - Install Laravel CLI and create the base project
2. **[Dev Container Setup](02-devcontainer-setup.md)** - Configure VS Code Dev Container environment
3. **[Debug Configuration](03-debug-configuration.md)** - Set up Xdebug for VSCode
4. **[Code Formatting](04-code-formatting.md)** - Configure Pint for PHP formatting
5. **[Laravel Data Package](05-laravel-data.md)** - Install Spatie Laravel Data for DTOs
6. **[TypeScript Transformer](06-typescript-transformer.md)** - Set up automatic type generation
7. **[Git Hooks](07-git-hooks.md)** - Configure Husky for pre-commit quality checks
8. **[IDE Helper](08-ide-helper.md)** - Install Laravel IDE Helper for autocompletion
9. **[Development Workflow](09-development-workflow.md)** - Create Composer scripts for common tasks
10. **[Type Inertia Shared Data](10-type-inertia-shared-data.md)** - Implement type-safe shared data for Inertia.js
11. **[Install Laravel Debugbar](11-install-laravel-debugbar.md)** - Add debugging tools for development
12. **[Frontend Code Quality Enhancement](12-frontend-code-quality-enhancement.md)** - Enhance ESLint and Prettier for better Vue.js development
13. **[E2E Testing](13-e2e-testing.md)** - Set up Playwright for end-to-end testing
14. **[Claude Code Rules](14-claude-code-rules.md)** - Configure coding conventions for AI-assisted development
15. **[Devtools](15-devtools.md)** - Helper scripts and Claude Code hooks for AI code review

## Quick Start

Once you've cloned this repository:

1. **Open in Dev Container**
   - Open the project in VS Code
   - Click "Reopen in Container" when prompted
   - Wait for the container to build and dependencies to install

2. **Run migrations**
   ```bash
   php artisan migrate
   ```

3. **Start development servers**
   ```bash
   composer dev
   ```

   This starts all services: Laravel server, Vite, queue worker, and logs.

4. **Visit your app**
   Open http://localhost:8080 in your browser

## Development Commands

### Using Direct Commands
```bash
# Run artisan commands directly
php artisan migrate
php artisan test

# Or use convenient aliases
art migrate
test
```

### Using Composer Scripts
```bash
# Start all dev servers at once
composer dev

# Set up IDE helpers and types
composer dev-setup

# Run tests
composer test
```

## Notes

- Each step builds upon the previous ones, so follow them in order
- Some steps require manual configuration that cannot be automated
- The documentation explains the reasoning behind each choice to help with future maintenance
- This starter kit does NOT use Laravel Sail - commands run directly without wrappers
