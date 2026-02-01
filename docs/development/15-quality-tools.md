# Quality Tools

## Overview

Running code checks manually is tedious and error-prone. Developers often forget to run tests after making changes, or spend time diagnosing cryptic error messages. This starterkit includes three quality tools that create a smart development workflow:

- **tarnished** - Tracks which checks need re-running after file changes
- **lumby** - Provides AI-powered diagnosis when commands fail
- **reldo** - Enables AI-powered code review before committing

Together, they ensure you always know what needs checking, get help when things fail, and catch issues before they become problems.

## Usage

### tarnished - Change Tracking

Tracks which quality checks need re-running after you modify files.

```bash
# Check what needs running
tarnished status
# Output: {"lint:php": "tarnished", "test:php": "clean", "lint:js": "clean"}

# After running a check that passes, it saves a checkpoint automatically
test:php
tarnished status
# Output: {"lint:php": "tarnished", "test:php": "clean", "lint:js": "clean"}
```

**Statuses:**
- `clean` - No changes since the check last passed
- `tarnished` - Files changed, need to re-run the check
- `never_saved` - Check has never been run successfully

### lumby - AI Diagnosis

Wraps commands and uses Claude to diagnose failures. When a command fails, lumby analyzes the output and suggests fixes.

```bash
# Automatically used by devtools scripts
test:php --filter=UserTest
# If tests fail, lumby provides AI-powered diagnosis

# Can be disabled
test:php --no-lumby
```

### reldo - Code Review

AI-powered code reviewer that checks your changes before committing.

```bash
# Review current changes
review:code "Review the authentication changes"

# Review specific files
review:code "Review app/Services/AuthService.php"
```

### Available Commands

| Command | Description |
|---------|-------------|
| `test:php` | Run PHPUnit tests with tarnished tracking |
| `lint:php` | Run PHPStan with tarnished tracking |
| `lint:js` | Run ESLint with tarnished tracking |
| `lint:ts` | Run TypeScript type checking |
| `review:code` | Run AI code review via reldo |
| `qa` | Run all quality checks |

All commands support `--no-lumby` to disable AI diagnosis.

### Workflow Example

```bash
# 1. Make some PHP changes
vim app/Models/User.php

# 2. Check what needs running
tarnished status
# {"lint:php": "tarnished", "test:php": "tarnished", "lint:js": "clean"}

# 3. Run the tarnished checks
lint:php
test:php

# 4. Verify all clean
tarnished status
# {"lint:php": "clean", "test:php": "clean", "lint:js": "clean"}

# 5. Get AI review before committing
review:code "Review User model changes"
```

### CI Integration

In CI environments without `ANTHROPIC_API_KEY`, lumby automatically disables itself:

```bash
# In CI, this just runs the command directly (no AI diagnosis)
test:php
```

The tarnished checkpoints still work, allowing you to skip unchanged checks in CI pipelines.

## Configuration

### Key Files

| File | Purpose |
|------|---------|
| `.tarnished/config.json` | Defines which files each profile tracks |
| `.reldo/settings.json` | Configures the AI code reviewer |
| `.reldo/orchestrator.md` | Defines the review workflow |

### tarnished Configuration

The `.tarnished/config.json` file defines which files each profile tracks:

```json
{
  "profiles": {
    "lint:php": {
      "patterns": [
        "app/**/*.php",
        "tests/**/*.php",
        "config/**/*.php",
        "database/**/*.php",
        "routes/**/*.php"
      ]
    },
    "lint:js": {
      "patterns": [
        "resources/js/**/*.vue",
        "resources/js/**/*.ts",
        "resources/js/**/*.tsx"
      ]
    },
    "test:php": {
      "patterns": [
        "app/**/*.php",
        "tests/**/*.php"
      ]
    }
  }
}
```

### reldo Configuration

The `.reldo/settings.json` configures the code reviewer:

```json
{
  "prompt": ".reldo/orchestrator.md",
  "model": "claude-sonnet-4-20250514",
  "timeout_seconds": 180,
  "allowed_tools": ["Read", "Glob", "Grep", "Bash", "Task", ...],
  "logging": {
    "enabled": true,
    "output_dir": ".reldo"
  }
}
```

The `.reldo/orchestrator.md` defines the review workflow:
- Checks tarnished status before reviewing
- Runs linters for changed file types
- Delegates to specialized reviewer agents (architecture-reviewer, frontend-reviewer)
- Aggregates results into a final PASS/FAIL status
