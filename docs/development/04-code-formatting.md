# Code Formatting

## Overview

Consistent code formatting improves readability, reduces merge conflicts, and maintains professional code quality across the project. This starterkit uses:

- **Laravel Pint** for PHP formatting (Laravel's coding standards)
- **Prettier** for JavaScript, TypeScript, and Vue formatting (with Tailwind CSS support)

Both tools are pre-configured and ready to use.

## Usage

### PHP Formatting

```bash
# Format all PHP files
composer format:php

# Format only modified files (faster, useful for pre-commit)
composer format:php-dirty
```

### JavaScript/Vue/TypeScript Formatting

```bash
# Format all frontend files in resources/
npm run format

# Check formatting without making changes
npm run format:check
```

### Format Everything

The `dev-setup` script runs both formatters along with other setup tasks:

```bash
composer dev-setup
```

## Configuration

### Key Files

| File | Purpose |
|------|---------|
| `.prettierrc` | Prettier configuration for JS/Vue/TS |
| `.prettierignore` | Files excluded from Prettier formatting |

### PHP (Pint)

Pint uses the Laravel preset by default. To customize, create a `pint.json` in the project root:

```json
{
  "preset": "laravel",
  "rules": {
    "array_syntax": { "syntax": "short" },
    "ordered_imports": true,
    "single_quote": true
  }
}
```

See the [Laravel Pint documentation](https://laravel.com/docs/pint) for available rules.

### Prettier

The `.prettierrc` configuration includes:

- Single quotes
- 4-space indentation (2 for YAML)
- Tailwind CSS class sorting (via `prettier-plugin-tailwindcss`)
- Automatic import organization (via `prettier-plugin-organize-imports`)

To modify Prettier behavior, edit `.prettierrc`. To exclude files from formatting, add patterns to `.prettierignore`.
