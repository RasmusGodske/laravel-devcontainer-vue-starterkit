# Project-Specific Frontend Rules

Add YOUR frontend rules here. These are NOT synced by the rules package.

## When to Add Rules

- Component patterns specific to your project
- Custom design system conventions
- Project-specific TypeScript patterns

## How to Create a Rule

1. Create a markdown file in this directory
2. Add YAML frontmatter with `paths` to specify when the rule loads
3. Write your rule content

## Example

Create `dashboard-components.md`:

```yaml
---
paths: resources/js/Pages/Dashboard/**/*.vue
---

# Dashboard Component Rules

Dashboard components must use the `DashboardLayout` wrapper.
All data fetching should use the `useDashboardData` composable.
```

## Notes

- Rules here will NOT be overwritten when running `php artisan dev-rules:update`
- The `paths` frontmatter determines when the rule auto-loads
- Rules without `paths` load for all files
