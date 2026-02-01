# Type-Safe Inertia Shared Data

## Overview

This starterkit provides type-safe shared data between Laravel and Vue through Inertia.js. Instead of manually maintaining TypeScript types that can drift from your backend, the shared data is defined using PHP Data classes that automatically generate TypeScript definitions.

Benefits:
- **Autocompletion** - IDE knows exactly what `page.props` contains
- **Compile-time errors** - TypeScript catches typos and missing properties
- **Single source of truth** - Change the PHP class, regenerate types, done

## Usage

### Accessing Shared Data in Vue Components

All shared data is available via `usePage()`:

```vue
<script setup lang="ts">
import { usePage } from '@inertiajs/vue3';

const page = usePage();

// Access shared props (fully typed!)
const appName = page.props.name;
const user = page.props.auth.user;
const quote = page.props.quote;
</script>
```

### Adding New Shared Props

1. **Update the Data class** in `app/Data/Inertia/InertiaSharedData.php`:

```php
public function __construct(
    public string $name,
    public InertiaQuoteData $quote,
    public InertiaAuthData $auth,
    public InertiaZiggyData $ziggy,
    public bool $sidebarOpen,
    public object $errors,
    public string $newProp,  // Add your new property
) {}
```

2. **Populate it** in `app/Http/Middleware/HandleInertiaRequests.php`:

```php
$inertiaSharedData = new InertiaSharedData(
    // ...existing props...
    newProp: 'your value here',
);
```

3. **Regenerate TypeScript types**:

```bash
composer dev-setup
```

Now `page.props.newProp` is available with full type safety in Vue.

## Configuration

### Key Files

| File | Purpose |
|------|---------|
| `app/Http/Middleware/HandleInertiaRequests.php` | Populates shared data for every Inertia response |
| `app/Data/Inertia/InertiaSharedData.php` | Main shared data structure |
| `app/Data/Inertia/InertiaAuthData.php` | Authentication data (current user) |
| `app/Data/Inertia/InertiaQuoteData.php` | Example: inspirational quote |
| `app/Data/Inertia/InertiaZiggyData.php` | Route information for frontend |
| `resources/js/types/generated.d.ts` | Auto-generated TypeScript definitions |

### Creating New Data Classes

For complex nested data, create a new Data class:

```php
<?php

namespace App\Data\Inertia;

use Spatie\LaravelData\Data;
use Spatie\TypeScriptTransformer\Attributes\TypeScript;

#[TypeScript()]
class InertiaNotificationsData extends Data
{
    public function __construct(
        public int $unreadCount,
        public array $recent,
    ) {}
}
```

Then add it to `InertiaSharedData` and populate it in the middleware.
