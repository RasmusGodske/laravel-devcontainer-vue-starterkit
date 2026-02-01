# Claude Code Rules

## Why This Step
When using Claude Code (Anthropic's CLI for Claude), having consistent coding conventions and patterns is crucial for AI-assisted development. The `.claude/rules` directory contains markdown files that Claude Code automatically reads to understand your project's conventions, coding standards, and architectural patterns.

Without these rules, Claude Code would generate code based on general best practices, which may not align with your specific project structure or team conventions. By providing explicit rules, you get:
- Consistent code generation that matches your existing codebase
- Reduced need for manual corrections after AI-generated code
- Better understanding of your tech stack specifics (Laravel, Vue, Inertia, etc.)

## What It Does
- Provides backend conventions for PHP/Laravel development (controllers, data classes, testing)
- Provides frontend conventions for Vue 3 with Composition API and TypeScript
- Documents Spatie Laravel Data patterns and validation approaches
- Defines naming conventions and code organization patterns
- Includes E2E testing conventions for Playwright
- Syncs rules from a centralized package to keep them up-to-date

## Implementation

### Install the Rules Package

The rules are managed via a Composer package that syncs convention files from a central repository:

```bash
composer require --dev rasmusgodske/godske-dev-rules
```

### Run the Sync Command

After installation, sync the rules to your project:

```bash
php artisan dev-rules:update
```

This creates the following structure:
```
.claude/rules/
└── techstack/
    ├── backend/           # PHP/Laravel conventions
    ├── dataclasses/       # Spatie Laravel Data patterns
    ├── e2e/               # Playwright testing conventions
    ├── frontend/          # Vue 3/TypeScript conventions
    ├── principles/        # General development principles
    └── python/            # Python development conventions
```

### Add Composer Script (Optional)

For convenience, add a script to `composer.json`:

```json
{
    "scripts": {
        "rules:update": "@php artisan dev-rules:update"
    }
}
```

Now you can update rules with:
```bash
composer rules:update
```

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

When the upstream rules package is updated, sync the latest changes:

```bash
composer update rasmusgodske/godske-dev-rules
composer rules:update
```

## Customizing Rules

The rules in `.claude/rules/techstack/` are synced from the package and will be overwritten on update. If you need project-specific rules:

1. Create a separate directory: `.claude/rules/project/`
2. Add your custom markdown files there
3. These won't be affected by `rules:update`

Claude Code reads all `.md` files in `.claude/rules/` recursively, so both `techstack/` and `project/` rules will be applied.
