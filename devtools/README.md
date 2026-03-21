# Development Tools

Scripts for common development tasks with integrated quality tracking.

## Available Commands

These commands are available as symlinks in the devcontainer:

**Testing & Linting:**

| Command | Script | Description |
|---------|--------|-------------|
| `test:php` | `test/php.sh` | Run PHPUnit tests |
| `lint:php` | `lint/php.sh` | Run PHPStan static analysis |
| `lint:js` | `lint/js.sh` | Run ESLint |
| `lint:ts` | `lint/ts.sh` | Run TypeScript type checking |
| `lint:deadcode` | `lint/deadcode.sh` | Run Knip dead code detection |
| `review:code` | `review/code.sh` | AI code review via reldo |
| `qa` | `qa.sh` | Run all quality checks |

**Sync Tools:**

| Command | Script | Description |
|---------|--------|-------------|
| `sync:models` | `sync/models.sh` | Regenerate model @property annotations |
| `sync:types` | `sync/types.sh` | Regenerate TypeScript types from PHP |
| `sync:routes` | `sync/routes.sh` | Regenerate Ziggy route types |
| `sync:all` | `sync/all.sh` | Run all sync scripts |

**Git Helpers (AI-assisted):**

| Command | Script | Description |
|---------|--------|-------------|
| `git:branch` | `git/branch.sh` | Create branch with type/slug naming |
| `git:commit` | `git/commit.sh` | Commit with AI-generated message |
| `git:pr` | `git/pr.sh` | Create PR with AI-generated description |

**Services & Orchestration:**

| Command | Script | Description |
|---------|--------|-------------|
| `dev:start` | `dev/start.sh` | Start full environment |
| `dev:stop` | `dev/stop.sh` | Stop services |
| `dev:status` | `dev/status.sh` | Show environment status |
| `service:serve` | `services/serve.sh` | Laravel dev server |
| `service:vite` | `services/vite.sh` | Vite HMR server |
| `service:database` | `services/database.sh` | PostgreSQL via Docker |
| `service:cache` | `services/cache.sh` | Redis via Docker |
| `service:desktop` | `services/desktop.sh` | Headed browser (noVNC) |
| `service:logs` | `services/logs.sh` | Laravel Pail log tailing |

## Directory Structure

```
devtools/
├── setup/              # Environment initialization (used by "Dev: Start")
│   ├── env.sh         # Create .env from .env.example
│   ├── composer.sh    # Install PHP dependencies
│   ├── npm.sh         # Install npm dependencies
│   ├── app-key.sh     # Generate APP_KEY
│   ├── migrated.sh    # Run migrations
│   └── configure-ports.sh  # Configure access & ports
├── lib/
│   └── queue.sh       # Shared flock-based test queue library
├── test/
│   └── php.sh         # PHPUnit + lumby + tarnished + queue
├── lint/
│   ├── php.sh         # PHPStan + lumby + tarnished
│   ├── js.sh          # ESLint + lumby + tarnished
│   ├── ts.sh          # vue-tsc + lumby
│   └── deadcode.sh    # Knip dead code detection + tarnished
├── git/                # AI-assisted git helpers
│   ├── branch.sh      # Create branches with type/slug naming
│   ├── commit.sh      # Commit with AI-generated messages
│   └── pr.sh          # Create PRs with AI-generated descriptions
├── sync/               # Generated artifact sync
│   ├── all.sh         # Run all sync scripts
│   ├── models.sh      # ide-helper:models (model annotations)
│   ├── types.sh       # typescript:transform (PHP → TS types)
│   └── routes.sh      # ziggy:generate (route types)
├── services/           # tmux-managed long-running services
│   ├── _lib.sh        # Shared service management library
│   ├── _env-watch.sh  # Auto-restart on .env changes
│   ├── serve.sh       # Laravel dev server
│   ├── vite.sh        # Vite HMR server
│   ├── database.sh    # PostgreSQL via Docker Compose
│   ├── cache.sh       # Redis via Docker Compose
│   ├── desktop.sh     # Xvfb + noVNC for headed browsers
│   └── logs.sh        # Laravel Pail log tailing
├── review/
│   └── code.sh        # reldo wrapper
├── qa.sh              # Run all quality checks
└── serve.sh           # Legacy server wrapper
```

## How It Works

Each command:
1. Runs the underlying tool (phpunit, phpstan, eslint, etc.)
2. Wraps with **lumby** for AI diagnosis on failure
3. Saves **tarnished** checkpoint on success

This means:
- When a check fails, you get AI-powered diagnosis
- After a check passes, tarnished knows it's "clean"
- `tarnished status` tells you what needs re-running

## Test Queue System

`test:php` uses a `flock`-based queue to prevent concurrent test runs from bottlenecking each other. When multiple sessions run tests simultaneously, only one executes at a time — the rest wait in line automatically.

### How It Works

1. The test script sources `devtools/lib/queue.sh` and initializes a queue
2. Before running tests, the script calls `queue_acquire` which attempts an exclusive `flock`
3. If the lock is held by another process, the caller **waits** (up to `--wait-timeout` seconds)
4. When tests finish, `queue_release` frees the lock and logs the run to history

### Runtime Data

Queue state is stored in the project directory:

| Path | Contents |
|------|----------|
| `devtools/test/.php/` | PHP test queue runtime data |
| `devtools/test/.php/lock` | flock lock file |
| `devtools/test/.php/status/` | Per-PID status files (JSON) |
| `devtools/test/.php/history.jsonl` | Run history log |

This directory is gitignored.

### Checking Queue Status

```bash
test:php --status    # Show who's running/waiting in PHP test queue
```

### Queue Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--status` | — | Show queue state and exit (does not run tests) |
| `--wait-timeout=N` | 600 | Max seconds to wait for queue lock before giving up |

### Using the Library in New Scripts

To add queue support to a new script:

```bash
#!/bin/bash
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"

source "$SCRIPT_DIR/../lib/queue.sh"
queue_init "$SCRIPT_DIR/.myqueue" "my-command"

# ... environment setup (outside the lock) ...

queue_acquire --timeout=600 --command="my-command $*"

# ... run your command ...
exit_code=$?

queue_release --exit-code=$exit_code
exit $exit_code
```

Key points:
- Environment setup (installing deps, etc.) runs **before** `queue_acquire` so it does not hold the lock
- Only the actual command execution is protected by the lock
- `queue_release` must be called before exiting to log history and clean up

## Usage Examples

```bash
# Run all PHP tests
test:php

# Run specific test
test:php --filter=UserTest

# Run tests in a directory
test:php tests/Feature/Auth/

# Check what needs running
tarnished status

# Sync generated artifacts
sync:all

# Get AI code review
review:code "Review authentication changes"

# Run all checks
qa
qa --compact                # Compact output for AI agents
qa --skip-deadcode          # Skip dead code detection

# Git helpers
git:branch feat "add login" # Create feat/add-login branch
git:commit                   # AI-generated commit message
git:pr                       # AI-generated PR description
```

## Disabling AI Diagnosis

All commands support `--no-lumby` to skip AI diagnosis:

```bash
test:php --no-lumby
lint:php --no-lumby
```

## Adding New Commands

1. Create script in appropriate directory (test/, lint/, review/)
2. Follow the pattern: run command → lumby wrap → tarnished checkpoint
3. Add symlink in `.devcontainer/Dockerfile`
4. Update this README
