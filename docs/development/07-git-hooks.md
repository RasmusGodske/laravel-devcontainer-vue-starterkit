# Git Hooks with Husky

## Overview

Git hooks run automated quality checks before your code enters the repository. This starterkit uses Husky to manage hooks that:

- **Format code automatically** - PHP files are formatted with Pint, so you never commit messy code
- **Lint frontend code** - ESLint runs on every commit to catch issues early
- **Verify PSR-4 compliance** - Pre-push checks ensure class names match file paths

These checks run automatically, so your team maintains consistent code standards without manual enforcement.

## Usage

### What Happens on Commit

When you run `git commit`, the pre-commit hook automatically:

1. Runs `./vendor/bin/pint --dirty` to format changed PHP files
2. Runs `npm run lint` to check frontend code
3. Stages any auto-fixed files
4. Allows the commit to proceed if all checks pass

### What Happens on Push

When you run `git push`, the pre-push hook:

1. Runs PSR-4 compliance check via Composer
2. Blocks the push if any class doesn't match PSR-4 autoloading standards

### Skipping Hooks

If you need to bypass hooks (use sparingly):

```bash
# Skip pre-commit hook
git commit --no-verify -m "Your message"

# Skip pre-push hook
git push --no-verify
```

## Configuration

### Key Files

| File | Purpose |
|------|---------|
| `.husky/pre-commit` | Runs formatting and linting before each commit |
| `.husky/pre-push` | Runs PSR-4 compliance check before pushing |
| `package.json` | Contains the `prepare` script that initializes Husky |

### Customization

To modify what runs on commit, edit `.husky/pre-commit`:

```bash
#!/bin/sh
echo "Running pre-commit checks..."

# Add your checks here
./vendor/bin/pint --dirty
npm run lint

# Stage auto-fixed files
git add -A

echo "Pre-commit checks passed!"
```

To add new hooks, create a file in `.husky/` named after the Git hook (e.g., `pre-push`, `commit-msg`).
