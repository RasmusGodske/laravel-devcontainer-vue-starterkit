# Git Hooks with Husky

## Why This Step
Husky manages Git hooks to enforce code quality standards before commits. This prevents poorly formatted or non-compliant code from entering the repository, maintaining consistent code standards across the entire team.

## What It Does
- Installs Husky for managing Git hooks
- Sets up pre-commit hooks for code formatting and PSR-4 compliance
- Automatically formats dirty files before committing
- Prevents commits when code doesn't meet quality standards

## Implementation

### Install Husky
```bash
npm install --save-dev husky
npx husky init
```

### Create Pre-Commit Hook for Code Formatting
Create `.husky/pre-commit`:

```bash
#!/bin/sh
echo "📋 Running pre-commit checks..."

# Run formatter on dirty files
./vendor/bin/pint --dirty

# Run frontend linting
npm run lint

# Stage any auto-fixed files
git add -A

echo "✅ Pre-commit checks passed!"
```

### Alternative: Create Pre-Commit Hook with PSR Compliance Check
If you want to add PSR-4 compliance checking:

.husky/pre-commit
```bash
#!/usr/bin/env sh
# Check for PSR compliance before committing

echo "📋 Running pre-commit checks..."

# Run the command, saving output to a file while displaying it
composer dump-autoload --dry-run -o --strict-psr 2>&1 | tee /tmp/composer_output.txt
STATUS=$?

# Check if we have PSR compliance errors
if grep -q "does not comply with psr-4 autoloading standard" /tmp/composer_output.txt; then
  echo ""
  echo "❌ PSR-4 compliance error detected! Please fix the file paths to match PSR-4 autoloading."
  echo "❌ Commit aborted."
  exit 1
elif [ $STATUS -ne 0 ]; then
  echo ""
  echo "❌ Error detected in autoload generation. Commit aborted."
  exit 1
else
  echo "✅ PSR compliance check passed!"
fi

# Clean up
rm -f /tmp/composer_output.txt
```