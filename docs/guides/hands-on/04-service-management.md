# Service Management

Managing long-running development services.

## Quick Reference

```bash
# Orchestration
dev:start                 # Start everything
dev:stop                  # Stop app services
dev:status                # Check all services

# Individual services
service:database start    # Start PostgreSQL
service:serve restart     # Restart Laravel server
service:vite logs 50      # View last 50 lines of Vite output
```

## Services Overview

| Service | Command | Description |
|---------|---------|-------------|
| Database | `service:database` | PostgreSQL via Docker |
| Cache | `service:cache` | Redis via Docker |
| Serve | `service:serve` | Laravel dev server |
| Vite | `service:vite` | Vite HMR server |
| Logs | `service:logs` | Laravel Pail log tailing |

## Service Commands

Each service supports the same subcommands:

### Start

```bash
service:serve start              # Start in background
service:serve start --attach     # Start and show output
```

### Stop

```bash
service:serve stop
```

### Restart

```bash
service:serve restart            # Restart in background
service:serve restart --attach   # Restart and show output
```

### Status

```bash
service:serve status             # Exit code 0 = running
```

### Logs

```bash
service:serve logs               # Show recent output
service:serve logs 100           # Show last 100 lines
service:serve logs --watch       # Follow logs continuously
service:serve logs 50 --watch    # Last 50 lines, then follow
```

### Attach

```bash
service:serve attach             # Attach to tmux session
```

Press `Ctrl+B` then `D` to detach.

## Orchestration Commands

### Start Everything

```bash
dev:start                        # Full setup + all services
dev:start --quick                # Skip setup, just start services
```

**Full start runs:**
1. Setup: .env, composer, npm, APP_KEY
2. Start: database, cache
3. Setup: migrations
4. Start: serve, vite, logs

### Stop Everything

```bash
dev:stop                         # Stop app services (serve, vite, logs)
dev:stop --all                   # Also stop database and cache
```

### Check Status

```bash
dev:status                       # Human-readable status
dev:status --json                # JSON output
dev:status --watch               # Auto-refresh every 2s
dev:status --watch=5             # Auto-refresh every 5s
```

## Troubleshooting

### Service Won't Start

Check if it's already running:
```bash
service:serve status
```

Check the logs:
```bash
service:serve logs 100
```

### Port Already in Use

```bash
# Find what's using port 8080
lsof -i :8080

# Kill it
kill -9 <PID>

# Or restart the service
service:serve restart
```

### Service Crashed

Check what happened:
```bash
service:serve logs 100
```

Restart it:
```bash
service:serve restart
```

### Database Connection Issues

Ensure database is running:
```bash
service:database status
service:database start
```

Check Docker:
```bash
docker ps | grep pgsql
```

### Vite Not Hot Reloading

Restart Vite:
```bash
service:vite restart
```

Check for errors:
```bash
service:vite logs --watch
```

## tmux Sessions

Services run in tmux sessions named `dev-*`:

```bash
tmux list-sessions
# dev-database: 1 windows
# dev-cache: 1 windows
# dev-serve: 1 windows
# dev-vite: 1 windows
# dev-logs: 1 windows
```

### Attach Directly

```bash
tmux attach -t dev-serve
```

### Detach

Press `Ctrl+B` then `D`

### Kill a Session

```bash
tmux kill-session -t dev-serve
```

## Scripts Location

All service scripts are in `devtools/`:

```
devtools/
├── dev/
│   ├── start.sh          # dev:start
│   ├── stop.sh           # dev:stop
│   └── status.sh         # dev:status
├── services/
│   ├── _lib.sh           # Shared tmux functions
│   ├── database.sh       # service:database
│   ├── cache.sh          # service:cache
│   ├── serve.sh          # service:serve
│   ├── vite.sh           # service:vite
│   └── logs.sh           # service:logs
└── setup/
    ├── env.sh            # Ensure .env exists
    ├── composer.sh       # Ensure vendor/ installed
    ├── npm.sh            # Ensure node_modules/ installed
    ├── app-key.sh        # Ensure APP_KEY set
    └── migrated.sh       # Ensure migrations run
```

## Next Steps

- [Dev Environment Overview](00-dev-environment.md)
- [Running Tests](01-running-tests.md)
