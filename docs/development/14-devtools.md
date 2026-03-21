# Devtools

## Overview

The devtools scripts provide a consistent interface for common development tasks like testing, linting, syncing, and code review. They integrate with the quality tools (tarnished, lumby, reldo) to enable:

- **Smart change tracking** - only run checks when files have changed
- **AI diagnosis** - get explanations when commands fail
- **Unified workflow** - same commands work locally and in CI

Instead of remembering different tool commands and flags, you use simple aliases like `test:php` and `lint:js` that handle the setup and integration automatically.

## Usage

### Testing & Linting

```bash
test:php                       # Run all tests
test:php --filter=UserTest     # Run specific test
lint:php                       # Run PHPStan static analysis
lint:js                        # Run ESLint
lint:ts                        # Run TypeScript type check
lint:deadcode                  # Run Knip dead code detection
review:code "Review changes"   # AI code review via reldo
qa                             # Run all quality checks
qa --compact                   # Compact output (for AI agents)
```

### Sync Tools

```bash
sync:models                    # Regenerate model @property annotations
sync:types                     # Regenerate TypeScript types from PHP
sync:routes                    # Regenerate Ziggy route types
sync:all                       # Run all sync scripts
```

### Git Helpers

AI-assisted git workflow tools using Claude CLI:

```bash
git:branch                     # Create branch with type/slug naming
git:branch feat "add login"   # Direct: creates feat/add-login
git:commit                     # Generate commit message from staged diff
git:commit "fix: login bug"   # Use provided message
git:pr                         # Generate PR title + description
git:pr -y                      # Auto-create without confirmation
```

### Service Management

```bash
service:serve start            # Start Laravel dev server
service:vite start             # Start Vite HMR server
service:database start         # Start PostgreSQL via Docker
service:cache start            # Start Redis via Docker
service:desktop start          # Start headed browser (noVNC)
service:logs start             # Start Laravel log tailing
```

Each service supports: `start`, `stop`, `restart`, `status`, `logs [N]`, `attach`

### QA (All Checks)

```bash
qa                             # Run all checks (Sync, ESLint, Dead Code, PHPStan, PHP Tests)
qa --compact                   # Compact output: only show failures
qa --skip-eslint               # Skip ESLint
qa --skip-deadcode             # Skip Dead Code detection
qa --skip-phpstan              # Skip PHPStan
qa --skip-php-tests            # Skip PHP tests
qa --skip-sync                 # Skip sync drift check
qa --exit-on-failure           # Stop on first failure
```

### Environment Orchestration

```bash
dev:start                      # Full setup + start all services
dev:start --quick              # Start services only (skip setup)
dev:stop                       # Stop app services (keep Docker)
dev:stop --all                 # Stop everything including Docker
dev:status                     # Show all service statuses
dev:status --json              # JSON output for scripts
dev:status --watch             # Live refresh every 2 seconds
```

## Configuration

### Directory Structure

```
devtools/
├── dev/                # Environment orchestration
│   ├── start.sh       # Full setup + services
│   ├── stop.sh        # Stop services
│   └── status.sh      # Show status
├── git/                # AI-assisted git helpers
│   ├── branch.sh      # Create branches with type/slug naming
│   ├── commit.sh      # Commit with AI-generated messages
│   └── pr.sh          # Create PRs with AI-generated descriptions
├── lib/
│   └── queue.sh       # Shared flock-based test queue
├── lint/
│   ├── php.sh         # PHPStan static analysis
│   ├── js.sh          # ESLint for Vue/TypeScript
│   ├── ts.sh          # TypeScript type checking
│   └── deadcode.sh    # Knip dead code detection
├── review/
│   └── code.sh        # AI code review via reldo
├── services/           # tmux-managed long-running services
│   ├── _lib.sh        # Shared service management library
│   ├── _env-watch.sh  # Auto-restart on .env changes
│   ├── serve.sh       # Laravel dev server (watches APP_PORT)
│   ├── vite.sh        # Vite HMR server (watches VITE_PORT)
│   ├── database.sh    # PostgreSQL via Docker Compose
│   ├── cache.sh       # Redis via Docker Compose
│   ├── desktop.sh     # Xvfb + noVNC for headed browsers
│   └── logs.sh        # Laravel Pail log tailing
├── setup/              # Environment initialization
│   ├── _lib.sh        # Shared tmux setup management
│   ├── env.sh         # Create .env from .env.example
│   ├── composer.sh    # Install Composer dependencies
│   ├── npm.sh         # Install npm dependencies
│   ├── app-key.sh     # Generate APP_KEY
│   ├── migrated.sh    # Run migrations and seeds
│   ├── configure-ports.sh  # Interactive port preset config
│   └── ci.sh          # CI environment setup
├── sync/               # Generated artifact sync
│   ├── all.sh         # Run all sync scripts
│   ├── models.sh      # ide-helper:models (model annotations)
│   ├── types.sh       # typescript:transform (PHP -> TS types)
│   └── routes.sh      # ziggy:generate (route types)
├── test/
│   └── php.sh         # PHPUnit test runner with queue
├── qa.sh              # Run all quality checks
└── serve.sh           # Legacy server wrapper
```

### Script Reference

| Alias | Script | Description |
|-------|--------|-------------|
| `test:php` | `test/php.sh` | Run PHPUnit tests |
| `lint:php` | `lint/php.sh` | Run PHPStan analysis |
| `lint:js` | `lint/js.sh` | Run ESLint |
| `lint:ts` | `lint/ts.sh` | Run TypeScript check |
| `lint:deadcode` | `lint/deadcode.sh` | Run Knip dead code detection |
| `review:code` | `review/code.sh` | AI code review |
| `qa` | `qa.sh` | Run all checks |
| `git:branch` | `git/branch.sh` | Create typed branches |
| `git:commit` | `git/commit.sh` | AI commit messages |
| `git:pr` | `git/pr.sh` | AI PR descriptions |
| `sync:models` | `sync/models.sh` | Sync model annotations |
| `sync:types` | `sync/types.sh` | Sync TypeScript types |
| `sync:routes` | `sync/routes.sh` | Sync Ziggy route types |
| `sync:all` | `sync/all.sh` | Run all sync scripts |
| `dev:start` | `dev/start.sh` | Start environment |
| `dev:stop` | `dev/stop.sh` | Stop environment |
| `dev:status` | `dev/status.sh` | Show status |

### Adding New Commands

To add a new devtools command:

1. **Create the script** in the appropriate directory (`test/`, `lint/`, `sync/`, etc.)
2. **Add a symlink** in the Dockerfile for easy access
3. **Integrate with quality tools** -- save `tarnished` checkpoints on success:

```bash
# Save checkpoint on success
if [ $exit_code -eq 0 ]; then
    tarnished save my:check 2>/dev/null || true
fi
```
