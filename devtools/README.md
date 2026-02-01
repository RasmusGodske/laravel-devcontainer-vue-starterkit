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
├── test/
│   └── php.sh         # PHPUnit + lumby + tarnished
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
