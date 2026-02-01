# Devtools

## Why This Step

Development tools and scripts that improve the developer experience. These provide a consistent interface for common tasks and integrate with the quality tools (tarnished, lumby, reldo) for smart change tracking and AI diagnostics.

## What It Does

- Provides helper scripts for environment setup and dependency management
- Organizes scripts by function (setup, test, lint, review)
- Integrates with quality tools for smart development workflow
- Creates symlinks for easy command access

## Directory Structure

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

## Key Components

### Setup Scripts

Used by the "Dev: Start" VS Code task to initialize the environment:

| Script | Purpose |
|--------|---------|
| `setup/env.sh` | Creates `.env` from `.env.example` if missing |
| `setup/composer.sh` | Installs/updates Composer dependencies |
| `setup/npm.sh` | Installs/updates npm dependencies |
| `setup/app-key.sh` | Generates `APP_KEY` if not set |
| `setup/migrated.sh` | Waits for DB, runs migrations and seeds |
| `setup/urls.sh` | Configures URLs for Codespaces vs local |

### Test & Lint Scripts

These integrate with the quality tools:

| Script | Command Alias | Description |
|--------|---------------|-------------|
| `test/php.sh` | `test:php` | Run PHPUnit tests |
| `lint/php.sh` | `lint:php` | Run PHPStan analysis |
| `lint/js.sh` | `lint:js` | Run ESLint |
| `lint/ts.sh` | `lint:ts` | Run TypeScript check |
| `review/code.sh` | `review:code` | AI code review |
| `qa.sh` | `qa` | Run all checks |

### Quality Tool Integration

Each test/lint script:
1. Sets up the environment if needed
2. Wraps the command with `lumby` for AI diagnosis on failure
3. Saves a `tarnished` checkpoint on success

Example from `test/php.sh`:
```bash
# Run with lumby wrapping
run_cmd php artisan test "$@"
exit_code=$?

# Save checkpoint on success
if [ $exit_code -eq 0 ]; then
    tarnished save test:php 2>/dev/null || true
fi
```

## Usage

### Using Command Aliases

The Dockerfile creates symlinks for easy access:

```bash
test:php                       # Run all tests
test:php --filter=UserTest     # Run specific test
lint:php                       # Run PHPStan
lint:js                        # Run ESLint
review:code "Review changes"   # AI code review
qa                             # Run all checks
```

### Using Scripts Directly

```bash
./devtools/test/php.sh --filter=UserTest
./devtools/lint/php.sh
./devtools/qa.sh --skip-phpstan
```

### Options

Most scripts support:
- `--no-lumby` - Skip AI diagnosis on failure
- `--help` - Show usage information

## VS Code Integration

The "Dev: Start" task uses these scripts in sequence:

1. `setup/env.sh` - Ensure .env exists
2. `setup/composer.sh` - Install PHP dependencies
3. `setup/app-key.sh` - Generate key if needed
4. `setup/npm.sh` - Install npm dependencies
5. Docker compose up - Start PostgreSQL and Redis
6. `setup/migrated.sh` - Run migrations
7. `setup/urls.sh` - Configure URLs
8. `serve.sh` - Start Laravel server
9. npm run dev - Start Vite

## Adding New Commands

1. Create script in appropriate directory (`test/`, `lint/`, etc.)
2. Add symlink in Dockerfile
3. Integrate with lumby and tarnished if appropriate
4. Document in this file
