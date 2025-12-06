# Development Workflow Scripts

## Why This Step
Composer scripts streamline common development tasks by bundling multiple commands into single, memorable shortcuts. This ensures consistency across the team and reduces the cognitive load of remembering complex command sequences.

## What It Does
- Creates a unified `dev-setup` script that generates all necessary files for development
- Combines TypeScript generation, IDE helper creation, and code formatting
- Provides a single command to prepare the development environment
- Ensures all generated files are properly formatted according to project standards

## Implementation

### Add Composer Scripts
Add the following scripts to your `composer.json` file under the `scripts` section:

```json
{
  ...
  "scripts": {
    ...
    "dev-setup": [
      "@php artisan typescript:transform --format",
      "@php artisan ide-helper:generate",
      "@php artisan ide-helper:models -W",
      "@php artisan ide-helper:meta",
      "@php artisan ziggy:generate --types resources/js/types/ziggy-auto-generated.js --types-only",
      "pint --dirty"
    ]
  }
}
```

**Note:** The `pint --dirty` command runs at the end because `ziggy:generate` produces unformatted code that needs to be cleaned up according to our formatting rules.

### Usage
Run the development setup script whenever you:
- Add new models or modify existing ones
- Update routes that need TypeScript definitions
- Want to refresh IDE autocompletion files
- Set up the project for a new developer

```bash
composer dev-setup
```