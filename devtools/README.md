# Development Tools

Scripts for common development tasks with integrated quality tracking.

## Available Commands

These commands are available as symlinks in the devcontainer:

| Command | Script | Description |
|---------|--------|-------------|
| `test:php` | `test/php.sh` | Run PHPUnit tests |
| `lint:php` | `lint/php.sh` | Run PHPStan static analysis |
| `lint:js` | `lint/js.sh` | Run ESLint |
| `lint:ts` | `lint/ts.sh` | Run TypeScript type checking |
| `review:code` | `review/code.sh` | AI code review via reldo |
| `qa` | `qa.sh` | Run all quality checks |

## Directory Structure

```
devtools/
├── setup/              # Environment initialization (used by "Dev: Start")
│   ├── env.sh         # Create .env from .env.example
│   ├── composer.sh    # Install PHP dependencies
│   ├── npm.sh         # Install npm dependencies
│   ├── app-key.sh     # Generate APP_KEY
│   ├── migrated.sh    # Run migrations
│   └── urls.sh        # Configure URLs
├── lib/
│   └── queue.sh       # Shared flock-based test queue library
├── test/
│   └── php.sh         # PHPUnit + lumby + tarnished + queue
├── lint/
│   ├── php.sh         # PHPStan + lumby + tarnished
│   ├── js.sh          # ESLint + lumby + tarnished
│   └── ts.sh          # vue-tsc + lumby
├── review/
│   └── code.sh        # reldo wrapper
├── qa.sh              # Run all quality checks
└── serve.sh           # Laravel server wrapper
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

# Get AI code review
review:code "Review authentication changes"

# Run all checks
qa
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
