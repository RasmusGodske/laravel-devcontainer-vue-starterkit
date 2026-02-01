# Development Environment Overview

This documentation covers the development environment features included in this Laravel + Vue starterkit.

## What's Included

| Category | Features |
|----------|----------|
| **Stack** | Laravel 12, Vue 3, Inertia.js, TypeScript, Tailwind CSS |
| **Environment** | VS Code Devcontainer (PHP runs directly, no Sail) |
| **Database** | PostgreSQL 17, Redis for caching/sessions |
| **Quality Tools** | tarnished, lumby, reldo for smart development workflows |
| **AI Integration** | Claude Code with rules, agents, and plugins |

## Quick Start

1. Open the project in VS Code
2. Click "Reopen in Container" when prompted
3. Run "Dev: Start" task (or `composer dev`)
4. Visit http://localhost:8080

## Documentation Index

### Foundation
- [Laravel + Vue Foundation](01-laravel-installation.md) - The pre-configured stack
- [Devcontainer Setup](02-devcontainer-setup.md) - Docker-based development environment
- [Debug Configuration](03-debug-configuration.md) - Xdebug for step-through debugging

### Code Quality
- [Code Formatting](04-code-formatting.md) - Pint and Prettier configuration
- [Git Hooks](07-git-hooks.md) - Automated pre-commit checks with Husky
- [Frontend Code Quality](12-frontend-code-quality-enhancement.md) - ESLint and TypeScript checking

### Type Safety
- [Laravel Data](05-laravel-data.md) - Type-safe DTOs with Spatie Laravel Data
- [TypeScript Transformer](06-typescript-transformer.md) - Auto-generate TypeScript from PHP
- [Type-Safe Inertia Shared Data](10-type-inertia-shared-data.md) - Typed shared props

### Developer Experience
- [IDE Helper](08-ide-helper.md) - Autocomplete for Laravel facades and models
- [Development Workflow](09-development-workflow.md) - Composer scripts for common tasks
- [Laravel Debugbar](11-install-laravel-debugbar.md) - Development insights

### Testing
- [E2E Testing](13-e2e-testing.md) - Playwright browser automation

### AI-Assisted Development
- [Devtools](14-devtools.md) - Development commands (test:php, lint:php, etc.)
- [Quality Tools](15-quality-tools.md) - tarnished, lumby, reldo integration
- [Claude Code Configuration](16-claude-code-configuration.md) - Rules, agents, and plugins

## Common Commands

```bash
# Start development
composer dev

# Run tests
test:php
test:php --filter=UserTest

# Lint code
lint:php                    # PHPStan
lint:js                     # ESLint

# Check what needs running
tarnished status

# AI code review
review:code "Review my changes"

# Run all quality checks
qa
```

## Why No Laravel Sail?

This starterkit runs PHP directly in the devcontainer instead of using Laravel Sail:

- **Faster execution** - No wrapper overhead
- **Better IDE integration** - PHP runs where your extensions run
- **Simpler debugging** - Xdebug in the same container
- **Lower resources** - One fewer container layer
