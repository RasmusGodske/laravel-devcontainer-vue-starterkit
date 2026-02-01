# TypeScript Transformer

## Overview

The Laravel TypeScript Transformer automatically generates TypeScript definitions from PHP classes, ensuring type safety between your Laravel backend and Vue.js frontend. This eliminates manual type maintenance and reduces runtime errors by keeping your backend and frontend types in sync.

Key benefits:
- **Type safety across the stack** - Changes to PHP Data objects, Models, or Enums automatically reflect in TypeScript
- **IDE autocompletion** - Get full IntelliSense for your backend types in Vue components
- **Reduced bugs** - Catch type mismatches at compile time instead of runtime

## Usage

### Generating Types

Run the artisan command to generate TypeScript definitions:

```bash
php artisan typescript:transform
```

This scans your PHP classes and outputs types to `resources/js/types/generated.d.ts`.

### Marking Classes for Transformation

Add the `#[TypeScript]` attribute to any class you want transformed:

```php
use Spatie\TypeScriptTransformer\Attributes\TypeScript;

#[TypeScript]
class User extends Authenticatable
{
    // Your model code
}
```

```php
use Spatie\LaravelData\Data;
use Spatie\TypeScriptTransformer\Attributes\TypeScript;

#[TypeScript]
class UserData extends Data
{
    public function __construct(
        public int $id,
        public string $name,
        public string $email,
    ) {}
}
```

### Using Generated Types in Vue

Import and use the generated types in your Vue components:

```vue
<script setup lang="ts">
import type { PropType } from 'vue';

// Types are available globally via the generated.d.ts file
const props = defineProps({
    user: {
        type: Object as PropType<App.Models.User>,
        required: true,
    },
    users: {
        type: Array as PropType<App.Data.UserData[]>,
        default: () => [],
    },
});
</script>
```

## Configuration

### Key Files

| File | Purpose |
|------|---------|
| `config/typescript-transformer.php` | Main configuration for type generation |
| `app/TypescriptTransformers/EloquentModelTransformer.php` | Custom transformer for Eloquent models |
| `resources/js/types/generated.d.ts` | Generated TypeScript output |

### Customization

**Adding directories to scan:**

Edit `auto_discover_types` in `config/typescript-transformer.php`:

```php
'auto_discover_types' => [
    app_path().'/Data',
    app_path().'/Models',
    app_path().'/Enums',
    app_path().'/YourNewDirectory', // Add new directories here
],
```

**Type replacements:**

Map PHP types to TypeScript types in `default_type_replacements`:

```php
'default_type_replacements' => [
    DateTime::class => 'string',
    Carbon\Carbon::class => 'string',
    // Add custom mappings
],
```

**Custom transformers:**

Add custom transformers to handle specific PHP classes. The included `EloquentModelTransformer` handles Eloquent models with relations, hidden attributes, and casts.