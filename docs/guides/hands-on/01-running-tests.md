# Running Tests

How to run PHPUnit tests using the devtools wrapper.

## Quick Reference

```bash
test:php                           # Run all tests
test:php --filter=UserTest         # Run specific test class
test:php --filter=test_user_can_login  # Run specific test method
```

## Why Use `test:php`?

The `test:php` command wraps PHPUnit with:
- **lumby** - AI diagnosis when tests fail
- **tarnished** - Tracks when tests need re-running

```bash
# These are equivalent, but test:php adds tracking
test:php
./vendor/bin/phpunit
php artisan test
```

## Filtering Tests

```bash
# By class name
test:php --filter=UserTest
test:php --filter=AuthenticationTest

# By method name
test:php --filter=test_user_can_login

# By file path
test:php tests/Feature/Auth/LoginTest.php

# Combine filters
test:php --filter=UserTest::test_user_can_login
```

## Common Options

```bash
test:php --stop-on-failure    # Stop at first failure
test:php --testdox            # Readable output format
test:php --coverage           # Generate coverage report
```

## Skipping AI Diagnosis

If you don't want lumby to analyze failures:

```bash
test:php --no-lumby
```

## Direct PHPUnit Access

For advanced options not exposed by the wrapper:

```bash
./vendor/bin/phpunit --help
./vendor/bin/phpunit --group=slow
./vendor/bin/phpunit --exclude-group=integration
```

## Test Organization

```
tests/
├── Feature/          # Integration tests (with database, HTTP)
│   ├── Auth/
│   ├── Api/
│   └── ...
├── Unit/             # Isolated unit tests
└── TestCase.php      # Base test class
```

## Database in Tests

Tests use a separate test database that's refreshed for each test:

```php
use Illuminate\Foundation\Testing\RefreshDatabase;

class UserTest extends TestCase
{
    use RefreshDatabase;

    public function test_user_can_register(): void
    {
        // Database is fresh for this test
    }
}
```

## Checking Test Status

```bash
tarnished status
# Shows if test:php is "clean" or "tarnished"
```

## Next Steps

- [Linting Code](02-linting-code.md)
- [Code Review](03-code-review.md)
