# Claude Code Rules

Rules are markdown files that auto-load based on file paths. They tell Claude Code about your project's conventions.

## Structure

```
rules/
├── techstack/          # Shared rules (synced via composer package)
│   ├── backend/        # PHP/Laravel conventions
│   ├── dataclasses/    # Spatie Laravel Data patterns
│   ├── e2e/            # Playwright testing conventions
│   ├── frontend/       # Vue 3/TypeScript conventions
│   ├── principles/     # Cross-cutting principles
│   └── python/         # Python development (if applicable)
└── project/            # Your custom rules (NOT synced)
    ├── backend/        # Project-specific PHP rules
    └── frontend/       # Project-specific Vue rules
```

## How Rules Work

Rules use YAML frontmatter to specify when they load:

```yaml
---
paths: app/**/*.php
---

# Rule content here...
```

- Edit a `.php` file → backend rules auto-load
- Edit a `.vue` file → frontend rules auto-load
- Rules without `paths` load for all files

## Updating Shared Rules

The `techstack/` rules come from a composer package. To update:

```bash
composer update rasmusgodske/godske-dev-rules
php artisan dev-rules:update
```

This will overwrite `techstack/` but NOT `project/`.

## Adding Custom Rules

Add your project-specific rules to `project/backend/` or `project/frontend/`.
See the README files in those directories for examples.
