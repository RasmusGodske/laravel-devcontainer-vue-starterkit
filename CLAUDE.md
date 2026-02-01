# CLAUDE.md - Laravel Vue Starterkit

## Project Overview

Laravel + Vue.js starter template with AI-assisted development tooling.

**Tech Stack:** Laravel 12, Vue 3, Inertia.js, PHP 8.3, TypeScript, Tailwind CSS

**Development Environment:** Devcontainer with PHP running directly (no Sail)

---

## Development Commands

Use the devtools scripts - they include change tracking and AI diagnosis:

| Command | Purpose |
|---------|---------|
| `test:php` | Run PHPUnit tests |
| `test:php --filter=Name` | Run specific test |
| `lint:php` | PHPStan static analysis |
| `lint:js` | ESLint |
| `lint:ts` | TypeScript type check |
| `review:code "prompt"` | AI code review via reldo |
| `qa` | Run all quality checks |
| `tarnished status` | See what checks need re-running |

**Starting the dev environment:**
- Use the "Dev: Start" VS Code task, or:
```bash
composer dev
```

---

## Quality Check Workflow

After making changes, always check what needs re-running:

```bash
tarnished status
# {"lint:php": "tarnished", "test:php": "tarnished", "lint:js": "clean"}

# Run the tarnished checks
lint:php
test:php

# Verify all clean
tarnished status
# {"lint:php": "clean", "test:php": "clean", "lint:js": "clean"}
```

**If a check is tarnished, run it before completing your task.**

---

## Code Conventions

### PHP/Laravel

- **Validation:** Use Data classes (Spatie Laravel Data), not FormRequests
- **Controllers:** Organize in nested directories by domain
- **Services:** Business logic goes in service classes
- **Testing:** Use factories, write feature tests

### Vue/TypeScript

- **Always:** `<script setup lang="ts">`
- **Composition API:** No Options API
- **Types:** Generate from PHP with `php artisan typescript:transform`

---

## Rules System

Rules in `.claude/rules/` auto-load based on file paths:

- `techstack/` - Shared conventions (synced via `php artisan dev-rules:update`)
- `project/` - Your custom rules (not synced)

To add a custom rule, create a file in `.claude/rules/project/backend/` or `frontend/` with:

```yaml
---
paths: app/Services/**/*.php
---

# Your rule content here
```

---

## Key Directories

```
.claude/           # Claude Code configuration
  rules/           # Auto-loading code conventions
  agents/          # Specialized task agents
  settings.json    # Permissions, plugins, MCP servers
.tarnished/        # Change tracking configuration
.reldo/            # Code review configuration
devtools/          # Development scripts (test, lint, review)
docs/development/  # Development environment documentation
```

---

## MCP Servers

- **laravel-boost** - Laravel tools (tinker, docs, database queries)
- **serena** - Semantic code navigation

---

## Plugins

The `liv-hooks` plugin provides validation:
- Blocks FormRequest usage (suggests Data classes)
- Enforces `<script setup lang="ts">` in Vue
- Validates E2E test paths
