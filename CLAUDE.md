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

## Dev Environment

### Orchestration Commands

| Command | Purpose |
|---------|---------|
| `dev:start` | Start everything (setup + services) - for CI/headless |
| `dev:start --quick` | Start services only (skip setup) |
| `dev:stop` | Stop app services (keeps Docker running) |
| `dev:stop --all` | Stop all services including Docker |
| `dev:status` | Show status of all services |

**Note:** For interactive development, use the VS Code "Dev: Start" task which shows each step in its own terminal. The `dev:start` script is designed for CI/headless environments.

### Service Commands

Long-running services run in tmux sessions, allowing both VS Code and Claude to access them.

| Service | Command | What it runs |
|---------|---------|--------------|
| Database | `service:database` | PostgreSQL via Docker |
| Cache | `service:cache` | Redis via Docker |
| Serve | `service:serve` | Laravel dev server (port 8080) |
| Vite | `service:vite` | Vite HMR dev server (port 5173) |
| Logs | `service:logs` | Laravel Pail log tailing |

Each service supports these subcommands:

```bash
service:serve start             # Start the service
service:serve start --attach    # Start and attach to see output
service:serve stop              # Stop the service
service:serve restart           # Restart the service
service:serve restart --attach  # Restart and attach
service:serve status            # Check if running (exit code 0 = running)
service:serve logs 50           # Show last 50 lines of output
service:serve logs --watch      # Follow logs continuously
service:serve logs 100 --watch  # Follow last 100 lines
service:serve attach            # Attach to tmux session (interactive)
```

### Checking Service Health

```bash
# Human-readable status
dev:status

# JSON output (for scripts/automation)
dev:status --json
# {"database": "running", "cache": "running", "serve": "running", "vite": "stopped", "logs": "stopped"}
```

### Troubleshooting

**User reports an error → Check the logs:**
```bash
service:serve logs 100    # See recent Laravel server output
service:logs start        # Start log tailing to watch for errors
```

**Service not responding → Restart it:**
```bash
service:serve restart
service:vite restart
```

**Check if services are healthy before running tests:**
```bash
dev:status --json | grep -q '"serve": "running"' && echo "Server is up"
```

### How It Works

Services run in named tmux sessions (`dev-database`, `dev-cache`, `dev-serve`, `dev-vite`, `dev-logs`). This means:

- **Persistence**: Services survive terminal closure
- **Shared access**: VS Code terminals and Claude can both see/control them
- **No duplicates**: Starting an already-running service just reports status
- **Logs available**: Output is captured in tmux scrollback buffer

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
