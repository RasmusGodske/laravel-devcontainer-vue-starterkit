# Project-Specific Backend Rules

Add YOUR backend rules here. These are NOT synced by the rules package.

## When to Add Rules

- Domain-specific conventions unique to your project
- Team preferences that differ from shared rules
- Project-specific patterns and constraints

## How to Create a Rule

1. Create a markdown file in this directory
2. Add YAML frontmatter with `paths` to specify when the rule loads
3. Write your rule content

## Example

Create `order-service.md`:

```yaml
---
paths: app/Services/Order/**/*.php
---

# Order Service Rules

All order operations must go through OrderService.
Never manipulate Order models directly from controllers.
```

## Notes

- Rules here will NOT be overwritten when running `php artisan dev-rules:update`
- The `paths` frontmatter determines when the rule auto-loads
- Rules without `paths` load for all files
