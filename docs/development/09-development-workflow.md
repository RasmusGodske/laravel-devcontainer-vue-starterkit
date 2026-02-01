# Development Workflow Scripts

## Overview

Composer scripts streamline common development tasks by bundling multiple commands into single, memorable shortcuts. Instead of remembering complex command sequences for generating TypeScript types, IDE helpers, and route definitions, you run one command. This ensures consistency across the team and reduces the cognitive load of context-switching between different tools.

## Usage

Run the development setup script whenever you:
- Add new models or modify existing ones
- Update routes that need TypeScript definitions
- Want to refresh IDE autocompletion files
- Set up the project for a new developer

```bash
composer dev-setup
```

This single command:
- Generates TypeScript types from PHP classes
- Creates IDE helper files for autocompletion
- Generates Ziggy route types
- Formats any generated code with Pint

## Configuration

### Key Files

| File | Purpose |
|------|---------|
| `composer.json` | Defines the `dev-setup` script under the `scripts` section |

### Customization

To modify what the `dev-setup` script does, edit the `scripts.dev-setup` array in `composer.json`. Each entry is a command that runs in sequence.

The script runs `pint --dirty` at the end because some generators (like Ziggy) produce unformatted code that needs cleanup.

To add your own workflow scripts, add new entries to the `scripts` section following the same pattern.
