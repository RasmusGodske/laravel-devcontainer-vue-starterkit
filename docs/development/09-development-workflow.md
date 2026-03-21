# Development Workflow Scripts

## Overview

Composer scripts streamline common development tasks by bundling multiple commands into single, memorable shortcuts. Instead of remembering complex command sequences for generating TypeScript types, IDE helpers, and route definitions, you run one command. This ensures consistency across the team and reduces the cognitive load of context-switching between different tools.

## Usage

### Individual Sync Commands

Sync generated artifacts individually when you change specific parts of the codebase:

```bash
sync:models    # Regenerate model @property annotations (ide-helper)
sync:types     # Regenerate TypeScript types from PHP enums/Data classes
sync:routes    # Regenerate Ziggy route type definitions
sync:all       # Run all three sync scripts
```

Each command integrates with tarnished -- after a successful sync, the checkpoint is saved so you know the artifacts are up to date.

### When to Run

| When you change... | Run |
|---------------------|-----|
| Database migrations or model relationships | `sync:models` |
| PHP enums or Data classes with `#[Typescript]` | `sync:types` |
| Route definitions | `sync:routes` |
| Multiple of the above | `sync:all` |

### Legacy: Composer Script

The `composer dev-setup` command still works and runs all sync scripts plus Pint formatting:

```bash
composer dev-setup
```

## Configuration

| File | Purpose |
|------|---------|
| `devtools/sync/models.sh` | ide-helper:models -W |
| `devtools/sync/types.sh` | typescript:transform --format |
| `devtools/sync/routes.sh` | ziggy:generate --types-only |
