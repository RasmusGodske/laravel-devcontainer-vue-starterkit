# Laravel IDE Helper

## Overview

Laravel IDE Helper provides intelligent autocompletion for Laravel's dynamic features. Without it, your IDE can't understand facades, model properties, or container bindings - leading to missing autocomplete suggestions and false "undefined method" warnings. With IDE Helper, you get full autocompletion for facades like `Cache::get()`, model attributes based on your database schema, and proper type hints throughout your Laravel code.

## Usage

### Regenerating Helper Files

Run these commands when you need to update the IDE helper files:

```bash
# Generate helper for facades and Laravel classes
php artisan ide-helper:generate

# Generate model annotations (based on database schema)
php artisan ide-helper:models --nowrite

# Generate PhpStorm meta file for container bindings
php artisan ide-helper:meta
```

### When to Run

- **After adding new models** - Run `ide-helper:models` to get property autocompletion
- **After migrations** - Run `ide-helper:models` since database columns changed
- **After installing new packages** - Run `ide-helper:generate` if the package adds facades

The `--nowrite` flag generates a separate helper file instead of writing annotations directly into your model files.

## Configuration

### Key Files

| File | Purpose |
|------|---------|
| `config/ide-helper.php` | All IDE Helper settings |
| `_ide_helper.php` | Generated facade helpers (git-ignored) |
| `_ide_helper_models.php` | Generated model helpers (git-ignored) |
| `.phpstorm.meta.php` | PhpStorm container resolution hints (git-ignored) |

### Customization

Common settings in `config/ide-helper.php`:

- `model_locations` - Directories to scan for models (default: `app`)
- `ignored_models` - Models to exclude from generation
- `write_model_magic_where` - Generate `whereColumn()` method hints
- `use_generics_annotations` - Use `Collection<User>` syntax in DocBlocks
- `post_migrate` - Commands to run automatically after migrations
