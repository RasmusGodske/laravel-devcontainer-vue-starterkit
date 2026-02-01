# Linting Code

Static analysis and code quality checks.

## Quick Reference

```bash
lint:php              # PHPStan static analysis
lint:js               # ESLint for Vue/TypeScript
lint:ts               # TypeScript type checking
```

## PHP Linting (PHPStan)

```bash
lint:php                          # Analyze all PHP code
lint:php app/Services/            # Analyze specific directory
lint:php app/Models/User.php      # Analyze specific file
```

PHPStan catches:
- Type mismatches
- Undefined methods/properties
- Dead code
- Potential null pointer issues

### Configuration

PHPStan config is in `phpstan.neon`. Current level: 5 (of 9).

### Fixing Issues

PHPStan issues usually require manual fixes. Common patterns:

```php
// Before: PHPStan complains about possible null
$user->name;

// After: Add null check
$user?->name;
// or
if ($user !== null) {
    $user->name;
}
```

## JavaScript/TypeScript Linting (ESLint)

```bash
lint:js                           # Lint all JS/TS/Vue files
lint:js resources/js/Pages/       # Lint specific directory
lint:js --fix                     # Auto-fix where possible
```

ESLint catches:
- Unused variables
- Missing imports
- Style violations
- Vue-specific issues

### Auto-fixing

Many ESLint issues can be auto-fixed:

```bash
lint:js --fix
```

## TypeScript Type Checking

```bash
lint:ts                           # Check all TypeScript
lint:ts --watch                   # Watch mode for development
```

TypeScript catches:
- Type errors
- Missing properties
- Incorrect function calls

### Generating Types from PHP

Keep TypeScript types in sync with PHP:

```bash
php artisan typescript:transform
```

This generates types in `resources/js/types/generated.d.ts`.

## Running All Linters

```bash
qa                    # Run all quality checks (tests + linting)
qa --skip-tests       # Skip tests, just run linters
```

## Checking Status

```bash
tarnished status
# Shows which linters need re-running
```

Example output:
```json
{"lint:php": "tarnished", "lint:js": "clean", "test:php": "clean"}
```

## Skipping AI Diagnosis

```bash
lint:php --no-lumby
lint:js --no-lumby
```

## IDE Integration

VS Code extensions provide real-time feedback:
- **PHP Intelephense** - PHP analysis
- **ESLint** - JavaScript/TypeScript linting
- **Vue - Official** - Vue file support

## Next Steps

- [Code Review](03-code-review.md)
- [Running Tests](01-running-tests.md)
