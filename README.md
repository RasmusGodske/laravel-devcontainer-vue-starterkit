# Laravel Devcontainer Vue Starterkit

A modern Laravel starter kit with Vue 3, Inertia.js, and Tailwind CSS, optimized for VS Code Dev Containers. This starter kit runs PHP directly in the devcontainer for optimal performance and IDE integration, without the overhead of Laravel Sail.

## Features

- **Vue 3**: Modern JavaScript framework for building user interfaces
- **Inertia.js**: Build single-page apps using classic server-side routing
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **TypeScript**: Static type checking for enhanced code quality
- **VS Code Dev Containers**: Fully configured development environment with PHP 8.x
- **PostgreSQL 17**: Production-ready database
- **Redis**: High-performance caching and session storage
- **Code Quality Tools**:
  - Laravel Pint for PHP formatting
  - Rector for automated code refactoring and import management
  - Larastan for static analysis
  - ESLint and Prettier for JavaScript/TypeScript
  - Husky for Git hooks
- **IDE Enhancements**:
  - Laravel IDE Helper for autocompletion
  - IntelliSense for Laravel routes and models
- **Debugging Tools**: Laravel Debugbar for development insights
- **Type-Safe Inertia Data**: Spatie Laravel Data with TypeScript transformer
- **Development Workflow**: Optimized composer scripts for common tasks

## Why No Laravel Sail?

This starter kit runs PHP directly in the devcontainer instead of using Laravel Sail, which provides several benefits:

- **Faster execution**: No container-to-container communication overhead
- **Better IDE integration**: PHP runs where your IDE extensions run
- **Simpler commands**: Use `php artisan` directly instead of `sail artisan`
- **Easier debugging**: Xdebug is in the same environment as your IDE
- **Lower resource usage**: One fewer container layer

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code

## Getting Started

### Method 1: Clone this repository

```bash
git clone https://github.com/RasmusGodske/laravel-devcontainer-vue-starterkit.git my-app
cd my-app
code .
```

When VS Code opens, click "Reopen in Container" when prompted, or use the command palette (F1) and select "Dev Containers: Reopen in Container".

The devcontainer will automatically:
1. Build the PHP development environment
2. Install composer dependencies
3. Install npm dependencies
4. Copy `.env.example` to `.env` and generate app key
5. Start PostgreSQL and Redis containers

### Method 2: Use as a template

1. Click "Use this template" on GitHub
2. Clone your new repository
3. Open in VS Code
4. Reopen in container

## First Steps After Setup

Once the devcontainer is ready:

1. **Run database migrations**:
   ```bash
   php artisan migrate
   ```

2. **Start the development servers**:
   ```bash
   composer dev
   ```

   This starts:
   - Laravel dev server on http://localhost:8080
   - Vite dev server with HMR
   - Queue worker
   - Log viewer (pail)

3. **Visit your app**: Open http://localhost:8080 in your browser

## Available Commands

### Composer Scripts

```bash
# Start all dev servers (artisan serve, vite, queue, logs)
composer dev

# Start with SSR support
composer dev:ssr

# Run tests
composer test

# Format PHP code
composer format:php

# Format only changed files
composer format:php-dirty

# Run Rector (dry-run to preview changes)
composer rector

# Run Rector and apply changes
composer rector:fix

# Complete dev setup (types, IDE helper, formatting)
composer dev-setup
```

### Artisan Commands (or use `art` alias)

```bash
# Run migrations
php artisan migrate

# Generate TypeScript types from PHP
php artisan typescript:transform

# Generate IDE helper files
php artisan ide-helper:generate

# Run tests
php artisan test
```

### Frontend Commands

```bash
# Start Vite dev server
npm run dev

# Build for production
npm run build

# Build SSR bundle
npm run build:ssr

# Lint and format
npm run lint
npm run format
```

## Development Workflow

### With Git Hooks

This starter kit includes Husky pre-commit hooks that automatically:
- Format PHP code with Pint
- Lint and format frontend code
- Stage any auto-fixes

### Database

The starter kit uses PostgreSQL by default. Connection details:
- Host: `pgsql`
- Port: `5432`
- Database: `laravel`
- Username: `laravel`
- Password: `password`

You can connect with any PostgreSQL client using these credentials.

### Caching and Sessions

Redis is configured for:
- Cache (`CACHE_STORE=redis`)
- Sessions (`SESSION_DRIVER=redis`)
- Queue (`QUEUE_CONNECTION=redis`)

### Type-Safe Inertia Shared Data

This starter kit includes type-safe shared data for Inertia using Spatie Laravel Data:

```php
// PHP - app/Data/Inertia/InertiaSharedData.php
class InertiaSharedData extends Data
{
    public function __construct(
        public InertiaAuthData $auth,
        public InertiaZiggyData $ziggy,
        public ?InertiaQuoteData $quote = null,
    ) {}
}
```

Generate TypeScript types:
```bash
php artisan typescript:transform
```

Use in Vue components with full type safety:
```vue
<script setup lang="ts">
import { usePage } from '@inertiajs/vue3';
import type { InertiaSharedData } from '@/types/generated';

const page = usePage<{ data: InertiaSharedData }>();
const user = page.props.auth.user; // Fully typed!
</script>
```

## Documentation

For detailed documentation on how this starter kit is configured, see the [docs/starter-kit](docs/starter-kit) directory.

## Architecture

```
┌─────────────────────────────────────────────┐
│  Host Machine                               │
│  ┌───────────────────────────────────────┐  │
│  │  Devcontainer                         │  │
│  │  - PHP 8.x                           │  │
│  │  - Node.js 20                        │  │
│  │  - Composer                          │  │
│  │  - VS Code Server                    │  │
│  │  - php artisan serve (port 8080)     │  │
│  └───────────────────────────────────────┘  │
│  ┌───────────────────────────────────────┐  │
│  │  PostgreSQL 17 Container              │  │
│  └───────────────────────────────────────┘  │
│  ┌───────────────────────────────────────┐  │
│  │  Redis Container                      │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

## Customization

### Change PHP Version

Edit `.devcontainer/Dockerfile` and update the base image or PHP version.

### Add PHP Extensions

Edit `.devcontainer/Dockerfile` and add to the `apt-get install` list.

### Add Services

Edit `docker-compose.yml` to add services like MySQL, Mailhog, etc.

## Troubleshooting

### Port 8080 already in use

Change the port in:
1. `.env`: `APP_URL=http://localhost:YOUR_PORT`
2. `.devcontainer/devcontainer.json`: Update `forwardPorts`
3. Composer scripts: Update `--port=YOUR_PORT` in dev commands

### Permission Issues

The devcontainer runs as the `vscode` user. If you encounter permission issues:

```bash
sudo chown -R vscode:vscode /home/vscode/project
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This starter kit is open-sourced software licensed under the [MIT license](LICENSE).
