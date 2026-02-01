# Claude Code Configuration

## Why This Step

Claude Code (Anthropic's CLI for Claude) benefits from project-specific configuration to work effectively. The `.claude/` directory contains settings, rules, and agents that customize Claude's behavior for your project.

Without this configuration:
- Claude would need to ask permission for every tool use
- Code generation would follow generic patterns instead of your conventions
- AI-assisted code review and quality checks wouldn't integrate smoothly

With proper configuration:
- Pre-approved permissions for safe operations (linting, testing, file reads)
- Consistent code generation matching your codebase patterns
- Integration with quality tools (tarnished, reldo, lumby)
- Specialized agents for common tasks

## What It Does

- Configures tool permissions to reduce permission prompts
- Integrates MCP servers (Laravel Boost, Serena)
- Enables liv-hooks plugin for code quality enforcement
- Provides coding convention rules via a synced package
- Includes specialized agents for engineering and review tasks

## Directory Structure

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

## Implementation

### 1. Settings Configuration

Create `.claude/settings.json` with permissions and integrations:

```json
{
  "statusLine": {
    "type": "command",
    "command": "/home/vscode/project/.claude/statusline-wrapper.sh"
  },
  "permissions": {
    "allow": [
      "Edit",
      "Write",
      "WebFetch",
      "WebSearch",
      "Glob",
      "Grep",
      "LS",
      "Read",
      "Bash(find:*)",
      "Bash(grep:*)",
      "Bash(cat:*)",
      "Bash(ls:*)",
      "Bash(sed:*)",
      "Bash(sort:*)",
      "Bash(uniq:*)",
      "Bash(head:*)",
      "Bash(tail:*)",
      "Bash(wc:*)",
      "Bash(cut:*)",
      "Bash(awk:*)",
      "Bash(xargs:*)",
      "Bash(tree:*)",
      "Bash(./vendor/bin/pint:*)",
      "Bash(./vendor/bin/phpstan:*)",
      "Bash(npm run type-check:files --:*)",
      "Bash(php artisan:*)",
      "Bash(composer:*)",
      "Bash(test:php:*)",
      "Bash(lint:php:*)",
      "Bash(lint:js:*)",
      "Bash(lint:ts:*)",
      "Bash(qa:*)",
      "Bash(review:code:*)",
      "Bash(tarnished:*)",
      "Bash(./devtools/test/php.sh:*)",
      "Bash(./devtools/lint/php.sh:*)",
      "Bash(./devtools/lint/js.sh:*)",
      "Bash(./devtools/lint/ts.sh:*)",
      "Bash(./devtools/qa.sh:*)",
      "Bash(./devtools/review/code.sh:*)",
      "Bash(reldo review:*)",
      "Bash(gh run view:*)",
      "Bash(gh pr view:*)",
      "Bash(git diff --name-only HEAD)",
      "Skill(*)",
      "mcp__laravel-boost",
      "mcp__serena"
    ]
  },
  "enabledMcpjsonServers": [
    "laravel-boost",
    "serena"
  ],
  "enabledPlugins": {
    "liv-hooks@claude-liv-conventions": true
  },
  "extraKnownMarketplaces": {
    "claude-liv-conventions": {
      "source": {
        "source": "github",
        "repo": "RasmusGodske/claude-liv-conventions"
      }
    }
  }
}
```

**Key sections:**

- **permissions.allow** - Pre-approved tools and commands (no prompts needed)
- **enabledMcpjsonServers** - MCP servers for Laravel-specific tools
- **enabledPlugins** - liv-hooks plugin for code quality enforcement
- **extraKnownMarketplaces** - Plugin source configuration

### 2. liv-hooks Plugin

The `liv-hooks@claude-liv-conventions` plugin provides hook-based code quality enforcement:

- Validates E2E test file paths follow conventions
- Reviews subagent task assignments
- Enforces project patterns during development

This replaces local Python hooks with a maintained community plugin.

### 3. Rules Setup

Rules tell Claude about your coding conventions. They're managed via a Composer package.

**Install the rules package:**

```bash
composer require --dev rasmusgodske/godske-dev-rules
```

**Sync rules to your project:**

```bash
php artisan dev-rules:update
```

This creates `.claude/rules/techstack/` with convention files:

```
techstack/
├── backend/           # PHP/Laravel conventions
├── dataclasses/       # Spatie Laravel Data patterns
├── e2e/               # Playwright testing conventions
├── frontend/          # Vue 3/TypeScript conventions
├── principles/        # General development principles
└── python/            # Python development conventions
```

**Add composer script (optional):**

```json
{
    "scripts": {
        "rules:update": "@php artisan dev-rules:update"
    }
}
```

### 4. Custom Project Rules

The `techstack/` rules are synced from the package and will be overwritten on update. For project-specific rules:

1. Create rules in `.claude/rules/project/backend/` or `.claude/rules/project/frontend/`
2. Add YAML frontmatter to specify when rules load:

```yaml
---
paths: app/Services/Order/**/*.php
---

# Order Service Rules

All order operations must go through OrderService.
Never manipulate Order models directly from controllers.
```

Claude Code reads all `.md` files in `.claude/rules/` recursively.

### 5. Agents

Create specialized agents in `.claude/agents/` for common tasks:

| Agent | Purpose |
|-------|---------|
| `software-engineer.md` | General implementation tasks |
| `frontend-engineer.md` | Vue/TypeScript work |
| `architecture-reviewer.md` | Design review |
| `e2e-reviewer.md` | E2E test review |
| `e2e-page-reviewer.md` | Page object review |
| `frontend-reviewer.md` | Frontend code review |
| `spec-completion-reviewer.md` | Spec implementation review |

Agents are markdown files with specialized instructions. Claude can delegate tasks to them.

## Key Rule Categories

### Backend Rules (`backend/`)
- `php-conventions.md` - Class imports, type hints, PHPDoc patterns
- `controller-conventions.md` - Controller structure, Inertia props, validation
- `form-data-classes.md` - Form Data Classes pattern for create/edit forms
- `database-conventions.md` - Migration patterns, column comments, enum handling
- `testing-conventions.md` - PHPUnit test structure, factory usage

### Frontend Rules (`frontend/`)
- `vue-conventions.md` - Vue 3 Composition API, `defineModel()`, TypeScript
- `component-composition.md` - Component splitting, single responsibility

### Data Class Rules (`dataclasses/`)
- `laravel-data.md` - Spatie Laravel Data patterns, validation annotations
- `custom-validation-rules.md` - Creating custom validation rules

### E2E Rules (`e2e/`)
- `test-conventions.md` - Playwright test structure
- `page-objects.md` - Page Object Model pattern
- `database-setup.md` - Test database management

## Updating Rules

When the upstream rules package is updated:

```bash
composer update rasmusgodske/godske-dev-rules
php artisan dev-rules:update
```

This overwrites `techstack/` but preserves `project/`.

## Integration with Quality Tools

The settings.json permissions integrate with quality tools from step 15:

- `Bash(test:php:*)` - Run PHPUnit with tarnished tracking
- `Bash(lint:php:*)` - Run PHPStan with tarnished tracking
- `Bash(review:code:*)` - Run reldo code review
- `Bash(tarnished:*)` - Check change tracking status

Claude can run these tools without permission prompts, enabling smooth AI-assisted development workflows.
