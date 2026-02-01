# Devtools

## Overview

The devtools scripts provide a consistent interface for common development tasks like testing, linting, and code review. They integrate with the quality tools (tarnished, lumby, reldo) to enable:

- **Smart change tracking** - only run checks when files have changed
- **AI diagnosis** - get explanations when commands fail
- **Unified workflow** - same commands work locally and in CI

Instead of remembering different tool commands and flags, you use simple aliases like `test:php` and `lint:js` that handle the setup and integration automatically.

## Usage

### Command Aliases

The container provides symlinks for easy access to all devtools:

```bash
test:php                       # Run all tests
test:php --filter=UserTest     # Run specific test
lint:php                       # Run PHPStan static analysis
lint:js                        # Run ESLint
lint:ts                        # Run TypeScript type check
review:code "Review changes"   # AI code review via reldo
qa                             # Run all quality checks
```

### Running Scripts Directly

You can also invoke scripts by path:

```bash
./devtools/test/php.sh --filter=UserTest
./devtools/lint/php.sh
./devtools/qa.sh --skip-phpstan
```

### Common Options

Most scripts support:

| Option | Description |
|--------|-------------|
| `--no-lumby` | Skip AI diagnosis on failure |
| `--help` | Show usage information |

### Quality Tool Integration

Each test/lint script automatically:

1. Wraps the command with `lumby` for AI diagnosis on failure
2. Saves a `tarnished` checkpoint on success

This means after running `lint:php`, tarnished knows that check is clean until you change PHP files.

## Configuration

### Directory Structure

```
devtools/
├── setup/              # Environment initialization
│   ├── env.sh         # Create .env from .env.example
│   ├── composer.sh    # Install/update Composer dependencies
│   ├── npm.sh         # Install/update npm dependencies
│   ├── app-key.sh     # Generate APP_KEY if missing
│   ├── migrated.sh    # Wait for DB, run migrations and seeds
│   └── urls.sh        # Configure URLs for Codespaces vs local
├── test/
│   └── php.sh         # PHPUnit test runner
├── lint/
│   ├── php.sh         # PHPStan static analysis
│   ├── js.sh          # ESLint for Vue/TypeScript
│   └── ts.sh          # TypeScript type checking
├── review/
│   └── code.sh        # AI code review via reldo
├── qa.sh              # Run all quality checks
└── serve.sh           # PHP server wrapper with restart handling
```

### Adding New Commands

To add a new devtools command:

1. **Create the script** in the appropriate directory (`test/`, `lint/`, etc.)
2. **Add a symlink** in the Dockerfile for easy access
3. **Integrate with quality tools** - wrap with `lumby` and save `tarnished` checkpoints:

```bash
# Run with lumby wrapping
run_cmd php artisan test "$@"
exit_code=$?

# Save checkpoint on success
if [ $exit_code -eq 0 ]; then
    tarnished save test:php 2>/dev/null || true
fi
```

### Script Reference

| Script | Alias | Description |
|--------|-------|-------------|
| `test/php.sh` | `test:php` | Run PHPUnit tests |
| `lint/php.sh` | `lint:php` | Run PHPStan analysis |
| `lint/js.sh` | `lint:js` | Run ESLint |
| `lint/ts.sh` | `lint:ts` | Run TypeScript check |
| `review/code.sh` | `review:code` | AI code review |
| `qa.sh` | `qa` | Run all checks |
