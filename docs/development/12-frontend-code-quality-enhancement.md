# Frontend Code Quality Enhancement

## Overview

This starterkit includes a carefully tuned ESLint and Prettier configuration that eliminates the common conflicts between linting and formatting tools. The setup ensures:

- **No ESLint/Prettier conflicts**: Vue formatting rules in ESLint are disabled to let Prettier handle all formatting
- **Consistent code style**: Trailing commas, bracket spacing, and arrow function parentheses are standardized
- **Modern JavaScript enforcement**: Rules like `prefer-const` and `no-var` catch outdated patterns
- **Tailwind class sorting**: Full support for utility functions like `cn()`, `clsx()`, `twMerge()`, and `cva()`

## Usage

### Daily Commands

```bash
# Check for linting errors
npm run lint

# Check if files are formatted correctly
npm run format:check

# Auto-format all files
npm run format
```

### What to Expect

- **Console and debugger statements** trigger warnings, not errors (convenient during development)
- **Unused variables** with underscore prefix (e.g., `_unused`) are ignored
- **Multi-line HTML attributes** are preserved - Prettier won't force single-line formatting
- **Trailing commas** are added automatically for cleaner git diffs

## Configuration

### Key Files

| File | Purpose |
|------|---------|
| `eslint.config.js` | ESLint rules for Vue, TypeScript, and general code quality |
| `.prettierrc` | Prettier formatting options with Vue and Tailwind support |

### ESLint Customization

The ESLint configuration includes Vue-specific rules disabled to prevent Prettier conflicts:

```javascript
rules: {
    // Vue formatting - let Prettier handle these
    'vue/max-attributes-per-line': 'off',
    'vue/html-indent': 'off',

    // TypeScript
    '@typescript-eslint/no-unused-vars': ['error', { 'argsIgnorePattern': '^_' }],

    // Code quality
    'no-console': 'warn',
    'prefer-const': 'error',
}
```

### Prettier Customization

Key Prettier options in `.prettierrc`:

```json
{
    "singleQuote": true,
    "printWidth": 150,
    "trailingComma": "all",
    "tailwindFunctions": ["clsx", "cn", "twMerge", "cva"]
}
```

To modify formatting behavior, edit `.prettierrc` directly. Common customizations:
- `printWidth`: Line length before wrapping (default: 150)
- `singleQuote`: Use single quotes for strings (default: true)
- `tabWidth`: Spaces per indentation level (default: 4)
