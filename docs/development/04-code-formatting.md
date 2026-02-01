# Code Formatting with Pint

## Why This Step
Laravel Pint ensures consistent code formatting across the project by automatically applying Laravel's coding standards. This improves code readability, reduces merge conflicts, and maintains professional code quality throughout the project lifecycle.

## What It Does
- Configures Laravel Pint with custom formatting rules
- Sets up Composer scripts for easy formatting commands
- Establishes consistent PHP code style across the entire project
- Provides both full project and "dirty files only" formatting options

## Implementation

### Create Pint Configuration
Create `pint.json` in the project root:

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

### Add Composer Scripts
Add the following to your `composer.json` file under the `scripts` section:

```json
{
  ...
  "scripts": {
    ...
    "format:php": "pint", 
    "format:php-dirty": "pint --dirty"
  }
}
```

The `format:php` command formats the entire codebase, while `format:php-dirty` only formats files that have been modified (useful for pre-commit hooks).