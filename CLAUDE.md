# CLAUDE.md - Laravel Vue Starterkit

## Project Overview

Laravel + Vue.js starter template with AI-assisted development tooling.

**Tech Stack:** Laravel 12, Vue 3, Inertia.js, PHP 8.3, TypeScript, Tailwind CSS

**Development Environment:** Devcontainer with PHP running directly (no Sail)

**⚠️ IMPORTANT:** This is a **LOCAL development environment** with test data. You do NOT have access to production systems. When debugging production issues reported by users, you can only review code, architecture, and logs - you cannot query production data.

---

## Agent System

### ⚠️ CRITICAL: Use `software-engineer` for Implementation

**NEVER write code directly.** When the user requests implementation work (creating features, fixing bugs, refactoring), delegate to the `software-engineer` agent.

| Task Type | Action |
|-----------|--------|
| Investigation, research, exploring code | Do directly |
| Understanding errors, reading logs | Do directly |
| Proposing solutions, discussing approaches | Do directly |
| **Writing/modifying code** | **Use `software-engineer` agent** |
| **Creating new files** | **Use `software-engineer` agent** |
| **Refactoring** | **Use `software-engineer` agent** |

**Why?** The `software-engineer` agent delegates to specialized engineers and uses `review:code` for code review, catching convention violations and issues before they become problems.

**How to invoke:**
```
Task(
  description: "Implement [brief description]",
  prompt: "[USER'S REQUEST WITH CONTEXT]",
  subagent_type: "software-engineer"
)
```

### Available Agents

| Agent | Purpose |
|-------|---------|
| `software-engineer` | Orchestrates implementation + review via `review:code` |
| `architecture-reviewer` | Reviews code organization and patterns |
| `frontend-engineer` | Vue/TypeScript implementation |
| `frontend-reviewer` | Reviews Vue/TypeScript code |

---

## ⚠️ CRITICAL: Alignment Before Implementation

**ALWAYS align with the user before writing code.** Never jump straight into implementation.

1. **Understand the Request**
   - Ask clarifying questions if anything is unclear
   - Confirm your understanding of the requirements
   - Identify any ambiguities or edge cases

2. **Propose a Solution**
   - Present your planned approach clearly and concisely
   - Explain which files you'll modify or create
   - Mention any architectural decisions or trade-offs
   - Wait for user approval before proceeding

3. **Stay Within Scope**
   - **ONLY implement what was explicitly requested or agreed upon**
   - **NEVER add "nice-to-have" features** without asking first
   - **DO NOT add fields, statuses, or features** that weren't discussed

4. **Seek Approval for Changes**
   - If you identify improvements during implementation, **STOP and ask** before adding them
   - What seems obvious to you may not align with the user's vision

---

## ⚠️ CRITICAL: Always Verify Quality Checks (Tarnished)

**Before completing ANY implementation task, run `tarnished status`** to see which checks need re-running.

### What is Tarnished?

**Tarnished** is a CLI tool that tracks which quality checks need re-running after code changes. It solves a critical problem: **Claude Code often forgets to run tests/linters after making changes**, leaving the codebase in an unknown state.

Think of it like this:
- When you **modify files**, those files become "tarnished" (dirty, needs checking)
- When you **run a check successfully**, those files become "clean" (verified working)
- Tarnished **remembers** which files were clean when each check last passed

### Why Does This Exist?

Without tarnished, this happens constantly:
1. Claude modifies 5 PHP files
2. Claude runs `test:php` - tests pass
3. Claude modifies 2 more PHP files
4. Claude says "Done!" - **but never re-ran tests after step 3**
5. User discovers broken tests later

With tarnished:
1. Claude modifies 5 PHP files → `test:php` becomes **tarnished**
2. Claude runs `test:php` - tests pass → `test:php` becomes **clean**
3. Claude modifies 2 more PHP files → `test:php` becomes **tarnished** again
4. Claude runs `tarnished status` → sees `test:php` is tarnished
5. Claude runs `test:php` again → tests pass → **clean**
6. Claude says "Done!" - with confidence everything works

### Profile Statuses

| Status | Meaning | Action |
|--------|---------|--------|
| `clean` | No files changed since check last passed | Safe to skip |
| `tarnished` | Files changed since last pass | **MUST re-run** |
| `never_saved` | Check has never passed | **MUST run** |

### Commands

```bash
tarnished status              # Check all profiles (use frequently!)
# {"lint:php": "tarnished", "lint:js": "clean", "test:php": "tarnished"}

tarnished check lint:php      # Check specific profile
# Exit code: 0 = clean, 1 = tarnished
```

### ⚠️ The Mindset

**If a check is tarnished, you MUST run it before completing your task.**

This is non-negotiable. The workflow is:
1. Make code changes
2. Run `tarnished status` to see what's tarnished
3. Run ALL tarnished checks relevant to your changes
4. If any check fails → **FIX IT** → re-run
5. Only mark your task complete when relevant profiles are clean

**Never say "Done" with tarnished checks.**

---

## Development Commands

Use the devtools scripts instead of raw commands. They include environment setup and AI-powered failure diagnosis via `lumby`:

| Command | Wraps | Accepts |
|---------|-------|---------|
| `test:php` | `php artisan test` | All artisan test flags (`--filter`, `--parallel`, file paths) |
| `lint:php` | `./vendor/bin/phpstan` | All PHPStan flags (`--generate-baseline`, etc.) |
| `lint:js` | ESLint | File paths |
| `lint:ts` | vue-tsc (TypeScript) | File paths |
| `review:code` | `reldo review` | `PROMPT` (positional), `--verbose`, `--exit-code` |
| `qa` | All checks | `--skip-phpstan`, `--skip-eslint` |

```bash
# PHP Tests
test:php                        # Run all tests
test:php --filter=TestName      # Run specific test(s)
test:php tests/Feature/Dir/     # Run tests in a directory

# Static Analysis
lint:php                        # Run PHPStan
lint:js                         # Run ESLint on all files
lint:ts                         # Run TypeScript type-check

# Code Review
review:code "Review my changes"           # AI code review
review:code "Review app/Models/" --verbose

# Run All Checks
qa                              # Run all quality checks
qa --skip-phpstan               # Skip PHPStan
```

**Why devtools?** These scripts auto-setup the environment and use `lumby` for AI diagnosis on failures—reducing context usage in your session.

### Test Queue System

`test:php` uses a queue to prevent concurrent runs from bottlenecking each other. If tests are already running, your run **waits automatically** — no action needed.

| Command | Purpose |
|---------|---------|
| `test:php --status` | Show who's running/waiting in the PHP test queue |
| `test:php --wait-timeout=N` | Set max wait time in seconds (default: 600) |

**For AI agents:** Do NOT kill or retry test processes that appear to be "hanging" — they may be waiting in the queue. Use `--status` to check. The queue handles serialization automatically.

---

## Dev Environment

### Starting the Environment

**VS Code Task (recommended):**
- Press `Ctrl+Shift+P` → "Tasks: Run Task" → "Dev: Start"

**CLI:**
```bash
dev:start              # Full setup + services
dev:start --quick      # Services only (skip setup)
```

### Orchestration Commands

| Command | Purpose |
|---------|---------|
| `dev:start` | Start everything (setup + services) |
| `dev:start --quick` | Start services only (skip setup) |
| `dev:stop` | Stop app services (keeps Docker running) |
| `dev:stop --all` | Stop all services including Docker |
| `dev:status` | Show status of all services |

### Service Commands

Long-running services run in tmux sessions, allowing both VS Code and Claude to access them.

| Service | Command | What it runs |
|---------|---------|--------------|
| Database | `service:database` | PostgreSQL via Docker |
| Cache | `service:cache` | Redis via Docker |
| Serve | `service:serve` | Laravel dev server (port 8080) |
| Vite | `service:vite` | Vite HMR dev server (port 5173) |
| Logs | `service:logs` | Laravel Pail log tailing |

Each service supports:

```bash
service:serve start             # Start the service
service:serve start --attach    # Start and attach to see output
service:serve stop              # Stop the service
service:serve restart           # Restart the service
service:serve status            # Check if running (exit code 0 = running)
service:serve logs 50           # Show last 50 lines of output
service:serve logs --watch      # Follow logs continuously
```

### Checking Service Health

```bash
dev:status                      # Human-readable status
dev:status --json               # JSON output for scripts
```

### Troubleshooting

**User reports an error → Check the logs:**
```bash
service:serve logs 100          # See recent Laravel server output
service:logs start              # Start log tailing to watch for errors
```

**Service not responding → Restart it:**
```bash
service:serve restart
service:vite restart
```

---

## Code Conventions

### PHP/Laravel

- **Validation:** Use Data classes (Spatie Laravel Data), not FormRequests
- **Controllers:** Organize in nested directories by domain
- **Services:** Business logic goes in service classes
- **Testing:** Use factories, write feature tests

### Vue/TypeScript

- **Always:** `<script setup lang="ts">`
- **Composition API:** No Options API
- **Types:** Generate from PHP with `php artisan typescript:transform`

---

## Rules System

Rules in `.claude/rules/` auto-load based on file paths via YAML frontmatter:

```yaml
---
paths: app/Services/**/*.php
---
# Rule content here...
```

**How it works:**
- Edit a `.php` file → backend rules auto-load
- Edit a `.vue` file → frontend rules auto-load
- Rules without `paths` frontmatter load for all files

**Directories:**
- `techstack/` - Shared conventions (synced via `php artisan dev-rules:update`)
- `project/` - Your custom rules (not synced)

---

## Key Directories

```
.claude/           # Claude Code configuration
  rules/           # Auto-loading code conventions
  agents/          # Specialized task agents
  hooks/           # Session hooks (user profile)
  skills/          # On-demand skills (/setup-profile)
  settings.json    # Permissions, plugins, MCP servers
.tarnished/        # Change tracking configuration
.reldo/            # Code review configuration
devtools/          # Development scripts (test, lint, review)
docs/guides/       # User guides (ai-first and hands-on)
docs/development/  # Technical documentation
```

---

## MCP Servers

- **laravel-boost** - Laravel tools (tinker, docs, database queries)
- **serena** - Semantic code navigation

---

## Plugins

The `liv-hooks` plugin provides validation:
- Blocks FormRequest usage (suggests Data classes)
- Enforces `<script setup lang="ts">` in Vue
- Validates E2E test paths
