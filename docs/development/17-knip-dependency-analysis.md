# Knip — Dependency Analysis

## Overview

[Knip](https://knip.dev/) analyzes the frontend dependency graph to find unused code and trace where files are used. It serves two purposes:

1. **Impact analysis** — "Before I change this file, what depends on it?"
2. **Dead code detection** — "What files, exports, and npm packages are unused?"

## Usage

### Check what depends on a file

```bash
# Vue components
npx knip --trace-file resources/js/components/MyComponent.vue

# Composables
npx knip --trace-file resources/js/composables/useMyComposable.ts

# Any frontend file
npx knip --trace-file resources/js/lib/utils.ts
```

Example output:

```
resources/js/components/MyComponent.vue:default
├── resources/js/pages/Dashboard.vue:importAs[default → MyComponent] ✓
└── resources/js/pages/Settings/Profile.vue:importAs[default → MyComponent] ✓
```

Empty output means nothing imports the file — it's dead code and safe to delete.

### Find unused code

```bash
# Full audit — unused files, exports, and npm packages
npx knip
```

This reports:
- **Unused files** — files not imported by anything
- **Unused exports** — exported functions/types nobody imports
- **Unused dependencies** — npm packages in `package.json` not used in code
- **Unlisted dependencies** — packages used in code but missing from `package.json`

## Configuration

Configuration lives in `knip.config.ts` at the project root.

### Key settings

| Setting | Purpose |
|---------|---------|
| `entry` | Starting points for dependency tracing (app.ts, pages) |
| `project` | All files Knip should analyze |
| `ignore` | Directories to skip (build artifacts, shadcn, generated types) |
| `compilers.vue` | Custom Vue SFC compiler (see below) |
| `vite: false` | Prevents Vite plugin from overriding entry point config |

### Custom Vue compiler

The config includes a custom Vue compiler that fixes a Knip limitation. Vue's `<script setup>` creates an implicit default export, but Knip's built-in regex compiler doesn't see it. Without the fix, `--trace-file` returns empty results for Composition API components.

The compiler adds a synthetic `export default {}` when processing `<script setup>` files, making all components traceable.

### shadcn components

The `resources/js/components/ui/` directory is ignored. shadcn components are vendored — not all are used by design, and flagging them as dead code is noise.

### Adding entry points

If you add new entry points (e.g., a separate admin app), add them to the `entry` array in `knip.config.ts`.

Shared components in `_components/` directories under `pages/` are automatically excluded from entry points so they show up correctly in dependency traces.

## Claude Code integration

A rule at `.claude/rules/techstack/frontend/check-dependencies-before-modifying.md` automatically reminds Claude to run `npx knip --trace-file` before modifying frontend files. This ensures Claude considers the impact of changes on dependent files.
