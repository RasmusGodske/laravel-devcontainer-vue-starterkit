# Quality Tools

## Why This Step

Running code checks manually is tedious and error-prone. Developers often forget to run tests after making changes, or spend time diagnosing cryptic error messages. The quality tools solve these problems:

- **tarnished** - Tracks which checks need re-running after file changes
- **lumby** - Provides AI-powered diagnosis when commands fail
- **reldo** - Enables AI-powered code review before committing

Together, they create a smart development workflow where you always know what needs checking, get help when things fail, and catch issues before they become problems.

## What It Does

- Installs three PyPI tools via `uv tool install` in the Dockerfile
- Creates symlinks for easy command access (`test:php`, `lint:php`, etc.)
- Integrates quality tracking into devtools scripts
- Enables AI diagnosis on command failures

## Tools Overview

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

## Available Commands

These symlinks are created in the Dockerfile:

| Command | Description |
|---------|-------------|
| `test:php` | Run PHPUnit tests with tarnished tracking |
| `lint:php` | Run PHPStan with tarnished tracking |
| `lint:js` | Run ESLint with tarnished tracking |
| `lint:ts` | Run TypeScript type checking |
| `review:code` | Run AI code review via reldo |
| `qa` | Run all quality checks |

All commands support `--no-lumby` to disable AI diagnosis.

## Implementation

### 1. Dockerfile Updates

The tools are installed for both vscode user and root (for CI):

```dockerfile
# Install quality tools via uv (vscode user)
USER vscode
RUN /home/vscode/.local/bin/uv tool install lumby
RUN /home/vscode/.local/bin/uv tool install reldo
RUN /home/vscode/.local/bin/uv tool install tarnished
USER root
RUN echo 'export PATH="$PATH:/home/vscode/.local/bin"' >> /home/vscode/.zshrc

# Install for root (CI environments)
RUN /root/.local/bin/uv tool install lumby \
    && /root/.local/bin/uv tool install reldo \
    && /root/.local/bin/uv tool install tarnished \
    && ln -s /root/.local/bin/lumby /usr/local/bin/lumby \
    && ln -s /root/.local/bin/reldo /usr/local/bin/reldo \
    && ln -s /root/.local/bin/tarnished /usr/local/bin/tarnished
```

### 2. Devtools Symlinks

```dockerfile
RUN ln -s /home/vscode/project/devtools/test/php.sh /usr/local/bin/test:php \
    && ln -s /home/vscode/project/devtools/lint/php.sh /usr/local/bin/lint:php \
    && ln -s /home/vscode/project/devtools/lint/js.sh /usr/local/bin/lint:js \
    && ln -s /home/vscode/project/devtools/lint/ts.sh /usr/local/bin/lint:ts \
    && ln -s /home/vscode/project/devtools/review/code.sh /usr/local/bin/review:code \
    && ln -s /home/vscode/project/devtools/qa.sh /usr/local/bin/qa
```

### 3. Devtools Structure

The devtools scripts are organized by function:

```
devtools/
├── setup/              # Environment setup
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
├── qa.sh              # Run all checks
└── serve.sh           # Laravel server wrapper
```

### 4. tarnished Configuration

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

### 5. reldo Configuration

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

The orchestrator ensures consistent, thorough reviews by coordinating multiple specialized agents.

## Workflow Example

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

## CI Integration

In CI environments without `ANTHROPIC_API_KEY`, lumby automatically disables itself:

```bash
# In CI, this just runs the command directly (no AI diagnosis)
test:php
```

The tarnished checkpoints still work, allowing you to skip unchanged checks in CI pipelines.
