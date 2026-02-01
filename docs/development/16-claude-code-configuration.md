# Claude Code Configuration

## Overview

Claude Code (Anthropic's CLI for Claude) benefits from project-specific configuration to work effectively. The `.claude/` directory contains settings, rules, and agents that customize Claude's behavior for your project.

Without this configuration, Claude would need to ask permission for every tool use and code generation would follow generic patterns instead of your conventions. With proper configuration:

- Pre-approved permissions for safe operations (linting, testing, file reads)
- Consistent code generation matching your codebase patterns
- Integration with quality tools (tarnished, reldo, lumby)
- Specialized agents for common tasks

## Usage

### Running Commands Without Prompts

With permissions configured, Claude can run quality tools directly:

```bash
# These commands are pre-approved - no permission prompts
lint:php
test:php
qa
review:code "Review the authentication flow"
```

### Using Agents

Delegate tasks to specialized agents:

| Agent | Purpose |
|-------|---------|
| `software-engineer.md` | General implementation tasks |
| `frontend-engineer.md` | Vue/TypeScript work |
| `architecture-reviewer.md` | Design review |
| `e2e-reviewer.md` | E2E test review |
| `e2e-page-reviewer.md` | Page object review |
| `frontend-reviewer.md` | Frontend code review |
| `spec-completion-reviewer.md` | Spec implementation review |

### Creating Custom Project Rules

For project-specific conventions, create rules in `.claude/rules/project/`:

```yaml
---
paths: app/Services/Order/**/*.php
---

# Order Service Rules

All order operations must go through OrderService.
Never manipulate Order models directly from controllers.
```

Claude Code reads all `.md` files in `.claude/rules/` recursively and loads them based on the `paths` frontmatter.

### Updating Shared Rules

When the upstream rules package is updated:

```bash
composer update rasmusgodske/godske-dev-rules
php artisan dev-rules:update
```

This overwrites `techstack/` but preserves `project/`.

## Configuration

### Key Files

| File | Purpose |
|------|---------|
| `.claude/settings.json` | Permissions, MCP servers, plugins |
| `.claude/agents/` | Specialized task agents |
| `.claude/rules/techstack/` | Shared conventions (synced from composer package) |
| `.claude/rules/project/` | Your custom rules (not synced) |

### Directory Structure

```
.claude/
├── settings.json          # Permissions, MCP servers, plugins
├── agents/                # Specialized task agents
│   ├── software-engineer.md
│   ├── frontend-engineer.md
│   ├── architecture-reviewer.md
│   └── ...
├── rules/                 # Coding conventions
│   ├── README.md
│   ├── techstack/         # Synced from composer package
│   │   ├── backend/
│   │   ├── frontend/
│   │   └── ...
│   └── project/           # Your custom rules (not synced)
│       ├── backend/
│       └── frontend/
└── statusline-wrapper.sh  # Status line script
```

### Settings Configuration

The `.claude/settings.json` contains:

- **permissions.allow** - Pre-approved tools and commands (no prompts needed)
- **enabledMcpjsonServers** - MCP servers for Laravel-specific tools
- **enabledPlugins** - liv-hooks plugin for code quality enforcement
- **extraKnownMarketplaces** - Plugin source configuration

### liv-hooks Plugin

The `liv-hooks@claude-liv-conventions` plugin provides hook-based code quality enforcement:

- Validates E2E test file paths follow conventions
- Reviews subagent task assignments
- Enforces project patterns during development

### Rule Categories

The `techstack/` rules cover:

| Category | Contents |
|----------|----------|
| `backend/` | PHP/Laravel conventions, controller structure, testing patterns |
| `frontend/` | Vue 3 Composition API, TypeScript, component splitting |
| `dataclasses/` | Spatie Laravel Data patterns, validation annotations |
| `e2e/` | Playwright test structure, Page Object Model |
| `principles/` | General development principles |
