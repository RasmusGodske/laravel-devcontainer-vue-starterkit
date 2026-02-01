# Laravel + Vue Foundation

## Overview

This starterkit comes with a pre-configured Laravel 12 and Vue 3 application, giving you a modern full-stack foundation out of the box. The stack includes:

- **Laravel 12** - PHP backend framework
- **Vue 3** - Reactive frontend framework with Composition API
- **Inertia.js** - Seamless Laravel-Vue integration without building an API
- **TypeScript** - Type-safe frontend development
- **Tailwind CSS** - Utility-first CSS framework
- **Vite** - Fast frontend build tooling

This foundation lets you start building features immediately instead of spending time on setup and configuration.

## Usage

With Inertia.js, you render Vue components directly from Laravel controllers:

```php
// app/Http/Controllers/DashboardController.php
use Inertia\Inertia;

public function index()
{
    return Inertia::render('Dashboard', [
        'stats' => $this->getStats(),
    ]);
}
```

The corresponding Vue component receives the data as props:

```vue
<!-- resources/js/Pages/Dashboard.vue -->
<script setup lang="ts">
import type { PropType } from 'vue';

interface Stats {
    users: number;
    orders: number;
}

const props = defineProps({
    stats: {
        type: Object as PropType<Stats>,
        required: true,
    },
});
</script>

<template>
    <div>
        <p>Users: {{ stats.users }}</p>
        <p>Orders: {{ stats.orders }}</p>
    </div>
</template>
```

### Starting Development

Use the VS Code "Dev: Start" task, or run:

```bash
composer dev
```

This starts the PHP server and Vite dev server together.

## Configuration

### Key Files

| File | Purpose |
|------|---------|
| `vite.config.ts` | Frontend build configuration |
| `tailwind.config.js` | Tailwind CSS customization |
| `tsconfig.json` | TypeScript compiler options |
| `config/inertia.php` | Inertia.js server-side settings |

### Customization

- **Add Vue plugins** in `resources/js/app.ts`
- **Configure Tailwind theme** in `tailwind.config.js`
- **Modify TypeScript settings** in `tsconfig.json`
