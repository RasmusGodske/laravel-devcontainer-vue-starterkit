# Code Review

AI-powered code review and quality assurance.

## Quick Reference

```bash
review:code "Review my changes"   # AI code review
qa                                # Run all quality checks
tarnished status                  # See what needs re-running
```

## AI Code Review

Use `review:code` to get AI feedback on your changes:

```bash
review:code "Review my changes"
review:code "Check for security issues"
review:code "Review the new user registration flow"
```

This uses **reldo** to analyze your code and provide feedback on:
- Code quality
- Potential bugs
- Security concerns
- Best practices

### Custom Review Focus

```bash
review:code "Focus on error handling"
review:code "Check for performance issues"
review:code "Review API endpoint security"
```

## Quality Assurance (qa)

The `qa` command runs all quality checks:

```bash
qa                    # Run everything
qa --skip-tests       # Skip PHPUnit tests
qa --skip-phpstan     # Skip PHPStan analysis
```

**What it runs:**
1. `lint:php` - PHPStan
2. `lint:js` - ESLint
3. `lint:ts` - TypeScript
4. `test:php` - PHPUnit

## Change Tracking (tarnished)

**tarnished** tracks which checks need re-running based on file changes.

### Check Status

```bash
tarnished status
```

Output:
```json
{
  "lint:php": "tarnished",
  "lint:js": "clean",
  "test:php": "tarnished"
}
```

- **clean** - Check passed, no relevant files changed since
- **tarnished** - Files changed, needs re-running

### How It Works

1. You run `lint:php` → passes → tarnished marks it "clean"
2. You edit a PHP file → tarnished marks `lint:php` as "tarnished"
3. You run `lint:php` again → passes → back to "clean"

### Configuration

Tarnished config is in `.tarnished/config.json`:

```json
{
  "checkpoints": {
    "lint:php": {
      "patterns": ["**/*.php"]
    },
    "lint:js": {
      "patterns": ["**/*.{js,ts,vue}"]
    }
  }
}
```

## Workflow Recommendations

### Before Committing

```bash
tarnished status              # See what's tarnished
lint:php                      # Fix PHP issues
lint:js --fix                 # Fix JS issues
test:php                      # Run tests
git commit                    # Now commit
```

Or let `qa` handle it:

```bash
qa                            # Run everything
git commit
```

### After Making Changes

```bash
tarnished status              # Quick check of what needs running
```

### CI Integration

The same commands work in CI:

```bash
qa                            # Fails if any check fails
```

## Error Diagnosis (lumby)

When checks fail, **lumby** provides AI diagnosis:

```
✗ test:php failed

lumby analysis:
The test_user_can_login test is failing because the User model
was changed to require email verification, but the test doesn't
verify the email first. Add $user->markEmailAsVerified() before
attempting login.
```

### Disable AI Diagnosis

```bash
lint:php --no-lumby
test:php --no-lumby
```

## Next Steps

- [Service Management](04-service-management.md)
- [Running Tests](01-running-tests.md)
