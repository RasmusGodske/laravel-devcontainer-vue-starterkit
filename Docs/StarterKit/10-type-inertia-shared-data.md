# Type Inertia Shared Data

## Why This Step
Inertia.js allows you to share data between your Laravel backend and Vue.js frontend seamlessly. This step focuses on creating dedicated data classes for the shared data, ensuring type safety and better organization of your Inertia responses. By defining these data classes, you can leverage TypeScript to catch errors at compile time rather than runtime, enhancing the overall developer experience.

## What It Does
- Defines a structured way to share data with Inertia.js
- Creates dedicated data classes for shared data
- Ensures type safety and autocompletion in your Vue.js components
- Simplifies the management of shared data across your application

## Implementation

### Create Data Classes
We will need to create several data classes that will be used to share data with Inertia.js. These classes will be placed in the `app/Data/Inertia` directory.

The following classes will be created:
- `InertiaAuthData`: Contains authentication-related data
- `InertiaQuoteData`: Contains a random quote to be displayed
- `InertiaSharedData`: Contains general shared data like application name and quote
- `InertiaZiggyData`: Contains Ziggy route data for frontend routing

Create the following data classes in the `app/Data/Inertia` directory:
```bash
mkdir -p app/Data/Inertia
```

Create `app/Data/Inertia/InertiaAuthData.php`:
```php
<?php

namespace App\Data\Inertia;

use App\Models\User;
use Spatie\LaravelData\Data;
use Spatie\TypeScriptTransformer\Attributes\TypeScript;

#[TypeScript()]
class InertiaAuthData extends Data
{
    public function __construct(
        public User $user,
    ) {}
}
```

Create `app/Data/Inertia/InertiaQuoteData.php`:
```php
<?php

namespace App\Data\Inertia;

use Spatie\LaravelData\Data;
use Spatie\TypeScriptTransformer\Attributes\TypeScript;

#[TypeScript()]
class InertiaQuoteData extends Data
{
    public function __construct(
        public string $message,
        public string $author,
    ) {}
}
```

Create `app/Data/Inertia/InertiaZiggyData.php`:
```php
<?php

namespace App\Data\Inertia;

use Illuminate\Http\Request;
use Spatie\LaravelData\Data;
use Spatie\TypeScriptTransformer\Attributes\TypeScript;
use Tighten\Ziggy\Ziggy;

/**
 * Represents the various available Ziggy routes and their configurations.
 * This data structure is used to provide route information to Inertia responses.
 *
 * This is used within resources/js/ssr.ts
 */
#[TypeScript()]
class InertiaZiggyData extends Data
{
    /**
     * @param  string  $url  The base URL for the Ziggy routes.
     * @param  int  $port  The port number for the Ziggy routes.
     * @return void
     */
    public function __construct(
        public string $url,
        public int $port,
        public array $defaults,
        public array $routes,
        public string $location,
    ) {}

    public static function fromZiggy(
        Ziggy $ziggy,
        Request $request,
    ): self {
        $arrayRepresentation = $ziggy->toArray();

        return new self(
            url: $arrayRepresentation['url'],
            port: $arrayRepresentation['port'],
            defaults: $arrayRepresentation['defaults'],
            routes: $arrayRepresentation['routes'],
            location: $request->url(),
        );
    }
}
```

Create `app/Data/Inertia/InertiaSharedData.php`:
```php
<?php

namespace App\Data\Inertia;

use Spatie\LaravelData\Data;
use Spatie\TypeScriptTransformer\Attributes\TypeScript;

/**
 * Represents Shared data that is accessible for all Inertia respoonses and is returned by the `HandleInertiaRequests` middleware.
 *
 * @see https://inertiajs.com/shared-data
 */
#[TypeScript()]
class InertiaSharedData extends Data
{
    public function __construct(
        public string $name,
        public InertiaQuoteData $quote,
        public InertiaAuthData $auth,
        public InertiaZiggyData $ziggy,
        public bool $sidebarOpen,
        public object $errors,
    ) {}
}
```

### Update Middleware to Share Data
Update the `app/Http/Middleware/HandleInertiaRequests.php` middleware to use the new data classes. Modify the `share` method to return an instance of `InertiaSharedData`:

```php
<?php

namespace App\Http\Middleware;

use App\Data\Inertia\InertiaAuthData;
use App\Data\Inertia\InertiaQuoteData;
use App\Data\Inertia\InertiaSharedData;
use App\Data\Inertia\InertiaZiggyData;
use Illuminate\Foundation\Inspiring;
use Illuminate\Http\Request;
use Inertia\Middleware;
use Tighten\Ziggy\Ziggy;

class HandleInertiaRequests extends Middleware
{
    /**
     * The root template that's loaded on the first page visit.
     *
     * @see https://inertiajs.com/server-side-setup#root-template
     *
     * @var string
     */
    protected $rootView = 'app';

    /**
     * Determines the current asset version.
     *
     * @see https://inertiajs.com/asset-versioning
     */
    public function version(Request $request): ?string
    {
        return parent::version($request);
    }

    /**
     * Define the props that are shared by default.
     *
     * @see https://inertiajs.com/shared-data
     *
     * @return array<string, mixed>
     */
    public function share(Request $request): array
    {
        [$message, $author] = str(Inspiring::quotes()->random())->explode('-');

        $inertiaAuthData = new InertiaAuthData(
            user: $request->user(),
        );

        $inertiaZiggyData = InertiaZiggyData::fromZiggy(
            ziggy: new Ziggy,
            request: $request,
        );

        $inertiaSharedData = new InertiaSharedData(
            name: config('app.name'),
            quote: new InertiaQuoteData(
                author: trim($author),
                message: trim($message),
            ),
            auth: $inertiaAuthData,
            sidebarOpen: ! $request->hasCookie('sidebar_state') || $request->cookie('sidebar_state') === 'true',
            ziggy: $inertiaZiggyData,
            errors: $this->resolveValidationErrors($request),
        );

        $inertiaSharedDataArray = $inertiaSharedData->toArray();

        return $inertiaSharedDataArray;
    }
}
```

### Generate TypeScript Definitions
To ensure that the TypeScript definitions for the shared data are generated, you need to run the TypeScript transformer command:

```bash
composer dev-setup
```

This will generate the Typescript definition based on the data classes you created. The generated TypeScript definitions will be placed in the `resources/js/types` directory, allowing you to use them in your Vue.js components.

### Update Inertia Shared Data typescript
The laravel installation comes with a default type that represents the Inertia Shared Data. However that type is static and would have to be manually updated every time you change the shared data. To avoid this, we will use the `spatie/typescript-transformer` package to automatically generate the TypeScript definitions based on the data classes.

By default the AppPageProps looks like this:
```typescript
// resources/js/types/index.d.ts
export type AppPageProps<T extends Record<string, unknown> = Record<string, unknown>> = T & {
    name: string;
    quote: { message: string; author: string };
    auth: Auth;
    ziggy: Config & { location: string };
    sidebarOpen: boolean;
};
```

And is used within `resources/js/types/globals.d.ts` which looks like this:
```typescript
import { AppPageProps } from '@/types/index';

// Extend ImportMeta interface for Vite...
declare module 'vite/client' {
    interface ImportMetaEnv {
        readonly VITE_APP_NAME: string;
        [key: string]: string | boolean | undefined;
    }

    interface ImportMeta {
        readonly env: ImportMetaEnv;
        readonly glob: <T>(pattern: string) => Record<string, () => Promise<T>>;
    }
}

declare module '@inertiajs/core' {
    interface PageProps extends InertiaPageProps, AppPageProps {}
}

declare module 'vue' {
    interface ComponentCustomProperties {
        $inertia: typeof Router;
        $page: Page;
        $headManager: ReturnType<typeof createHeadManager>;
    }
}
```

We want to change `resources/js/types/globals.d.ts` to use the generated TypeScript definitions instead of the static ones

Override `resources/js/types/globals.d.ts` to look like this:
```typescript
import type { Config } from 'ziggy-js';

// Extend ImportMeta interface for Vite...
declare module 'vite/client' {
    interface ImportMetaEnv {
        readonly VITE_APP_NAME: string;
        [key: string]: string | boolean | undefined;
    }

    interface ImportMeta {
        readonly env: ImportMetaEnv;
        readonly glob: <T>(pattern: string) => Record<string, () => Promise<T>>;
    }
}


export type AppPageProps = App.Data.Inertia.InertiaSharedData & {
    // Use the original Ziggy type from ziggy-js instead of our own Config type
    ziggy: Config & { location: string };
};

declare module '@inertiajs/core' {
    interface PageProps extends InertiaPageProps, AppPageProps {}
}

declare module 'vue' {
    interface ComponentCustomProperties {
        $inertia: typeof Router;
        $page: Page;
        $headManager: ReturnType<typeof createHeadManager>;
    }
}
```

### Delete Old TypeScript Definitions
To avoid conflicts with the old TypeScript definitions, delete the `resources/js/types/index.d.ts` file. The new definitions will be generated automatically based on the data classes you created.


Delete the following from `resources/js/types/index.d.ts`:
```typescript
export type AppPageProps<T extends Record<string, unknown> = Record<string, unknown>> = T & {
    name: string;
    quote: { message: string; author: string };
    auth: Auth;
    ziggy: Config & { location: string };
    sidebarOpen: boolean;
};

export interface User {
    id: number;
    name: string;
    email: string;
    avatar?: string;
    email_verified_at: string | null;
    created_at: string;
    updated_at: string;
}
```

Since we deleted the `User` type is no longer needed as we have an auto generated type for the `User` model within resources/js/types/generated.d.ts. 

Also remove the unused `Config` import from `resources/js/types/index.d.ts`:
```typescript
// Remove this line:
import type { Config } from 'ziggy-js';
```

We should also update the following files to remove the old `User` type:
Update `resources/js/types/globals.d.ts` to remove the old `User` type:

`resources/js/components/UserInfo.vue`:
```js
<script setup lang="ts">
import type { User } from '@/types'; // DELETE THIS
import { computed } from 'vue';

interface Props {
    user: User; // DELETE THIS
    // Change to use the auto-generated User type
    user: App.Models.User; // Update to use the auto-generated User type
    showEmail?: boolean;
}

</script>
```

`resources/js/components/NavUser.vue`:
```js
<script setup lang="ts">
import UserInfo from '@/components/UserInfo.vue';
import { DropdownMenu, DropdownMenuContent, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { SidebarMenu, SidebarMenuButton, SidebarMenuItem, useSidebar } from '@/components/ui/sidebar';
//import { type User } from '@/types'; // DELETE THIS
import { usePage } from '@inertiajs/vue3';
import { ChevronsUpDown } from 'lucide-vue-next';
import UserMenuContent from './UserMenuContent.vue';

const page = usePage();
//const user = page.props.auth.user as User; // DELETE THIS
const user = page.props.auth.user; // Update to use the auto-generated User type (Not we don't need to cast it to User anymore)
const { isMobile, state } = useSidebar();
</script>
```

`resources/js/components/UserMenuContent.vue`:
```js
<script setup lang="ts">
import UserInfo from '@/components/UserInfo.vue';
import { DropdownMenuGroup, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
// import type { User } from '@/types'; // DELETE THIS
import { Link, router } from '@inertiajs/vue3';
import { LogOut, Settings } from 'lucide-vue-next';

interface Props {
    user: User; // DELETE THIS
    // Change to use the auto-generated User type
    user: App.Models.User; // Update to use the auto-generated User type
}

</script>
```

`resources/js/pages/settings/Profile.vue`:
```js
<script setup lang="ts">
import { Head, Link, useForm, usePage } from '@inertiajs/vue3';

import DeleteUser from '@/components/DeleteUser.vue';
import HeadingSmall from '@/components/HeadingSmall.vue';
import InputError from '@/components/InputError.vue';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import AppLayout from '@/layouts/AppLayout.vue';
import SettingsLayout from '@/layouts/settings/Layout.vue';
// import { type BreadcrumbItem, type User } from '@/types'; // DELETE THIS
import { BreadcrumbItem } from '@/types';

interface Props {
    mustVerifyEmail: boolean;
    status?: string;
}

defineProps<Props>();

const breadcrumbItems: BreadcrumbItem[] = [
    {
        title: 'Profile settings',
        href: '/settings/profile',
    },
];

const page = usePage();
// const user = page.props.auth.user as User; // DELETE THIS
const user = page.props.auth.user as App.Models.User; // Update to use the auto-generated User type

</script>
```