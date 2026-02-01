# Dev Environment

Overview of how the development environment works.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Devcontainer                                       │
│  ┌─────────────────────────────────────────────┐   │
│  │  PHP 8.3 + Node.js 20 + Tools               │   │
│  │  - Laravel dev server (port 8080)           │   │
│  │  - Vite HMR (port 5173)                     │   │
│  │  - All CLI tools (composer, npm, etc.)      │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────┐  ┌─────────────────┐          │
│  │  PostgreSQL 17  │  │  Redis          │          │
│  │  (Docker)       │  │  (Docker)       │          │
│  └─────────────────┘  └─────────────────┘          │
└─────────────────────────────────────────────────────┘
```

PHP runs directly in the devcontainer (no Sail). Docker is only used for PostgreSQL and Redis.

## Services

Long-running services run in tmux sessions:

| Service | Command | Port | What It Runs |
|---------|---------|------|--------------|
| Database | `service:database` | 5432 | PostgreSQL via Docker |
| Cache | `service:cache` | 6379 | Redis via Docker |
| Serve | `service:serve` | 8080 | `php artisan serve` |
| Vite | `service:vite` | 5173 | Vite dev server with HMR |
| Logs | `service:logs` | - | Laravel Pail log tailing |

## Starting Everything

**VS Code Task (recommended):**
- Press `Ctrl+Shift+P` → "Tasks: Run Task" → "Dev: Start"

**CLI:**
```bash
dev:start              # Full setup + services
dev:start --quick      # Services only (skip setup)
```

## Stopping Everything

**VS Code Task:**
- "Dev: Stop"

**CLI:**
```bash
dev:stop               # Stop app services (keeps Docker)
dev:stop --all         # Stop everything including Docker
```

## Checking Status

```bash
dev:status             # Human-readable status
dev:status --json      # JSON output for scripts
dev:status --watch     # Auto-refresh every 2s
```

## Why tmux?

Services run in tmux sessions so:
- They persist when terminals close
- Both VS Code and Claude can access them
- No duplicate processes
- Logs are captured and accessible

See [Service Management](04-service-management.md) for detailed service commands.

## Database Connection

| Setting | Value |
|---------|-------|
| Host | `pgsql` (from container) or `localhost` (from host) |
| Port | 5432 |
| Database | `laravel` |
| Username | `laravel` |
| Password | `password` |

## Next Steps

- [Running Tests](01-running-tests.md)
- [Service Management](04-service-management.md)
