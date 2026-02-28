---
paths: resources/js/**/*.{vue,ts,tsx,js}
---

# Check Dependencies Before Modifying Frontend Files

> **Before modifying a Vue component, composable, or utility, check what depends on it.**

## The Rule

When you are about to modify or delete a file in `resources/js/`, run:

```bash
npx knip --trace-file <path-to-file>
```

This shows every file that imports the target file's exports.

## When to Run

| Situation | Run trace? |
|-----------|:---:|
| Modifying a component's props, emits, or public API | Yes |
| Renaming or moving a file | Yes |
| Deleting a file | Yes |
| Changing a composable's return type or signature | Yes |
| Internal-only changes (template tweaks, local state) | No |

## Reading the Output

```bash
npx knip --trace-file resources/js/Components/App/ActivityModal.vue
```

```
resources/js/Components/App/ActivityModal.vue:default
├── resources/js/Pages/App/Orders/Index.vue:importAs[default → ActivityModal] ✓
├── resources/js/Pages/App/Orders/Show.vue:importAs[default → ActivityModal] ✓
└── resources/js/Pages/App/Products/Index.vue:importAs[default → ActivityModal] ✓
```

- Each line is a file that imports this component
- Empty output = nothing imports it (dead code, safe to delete)

## What to Do With the Results

- **Changing props/emits?** Verify all consumers pass the updated contract
- **Renaming?** Update all import paths shown
- **Deleting?** Empty output confirms it's safe; non-empty means you'll break things
- **Many consumers?** Consider backward compatibility or update all callers
