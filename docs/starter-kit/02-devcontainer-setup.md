# VS Code Dev Container Setup

## Why This Step
VS Code Dev Containers provide a fully configured development environment that runs inside Docker. Unlike Laravel Sail, PHP runs directly in the devcontainer where your IDE and extensions operate, providing better performance, simpler commands, and seamless IDE integration.

## What It Does
- Creates a devcontainer with PHP, Composer, and Node.js pre-installed
- Configures Docker services for PostgreSQL and Redis
- Sets up the development environment with proper networking and volume mounting
- Enables running Laravel artisan commands directly without any wrapper
- Configures VS Code extensions and settings automatically

## Why Not Laravel Sail?

This starter kit intentionally does not use Laravel Sail because:

1. **Redundant containerization**: When using devcontainers, Sail creates an extra container layer
2. **Performance overhead**: Commands go through `sail` wrapper instead of running directly
3. **IDE disconnect**: Your IDE runs in devcontainer but PHP runs in Sail container
4. **Complexity**: Debugging requires extra configuration for the additional layer

By running PHP directly in the devcontainer, you get:
- Faster command execution (`php artisan` vs `sail artisan`)
- Better IDE integration (IntelliSense, debugging)
- Simpler mental model
- Lower resource usage

## Implementation

### Prerequisites
- Docker Desktop installed
- VS Code with Dev Containers extension

### Open in Dev Container

1. Clone the repository
2. Open in VS Code
3. Click "Reopen in Container" when prompted, or use Command Palette (F1) → "Dev Containers: Reopen in Container"

The devcontainer will automatically:
- Build the development environment
- Install PHP dependencies via composer
- Install Node dependencies via npm
- Create `.env` file and generate app key
- Start PostgreSQL and Redis containers

### What Gets Installed

The devcontainer includes:
- **PHP 8.x** with extensions:
  - pgsql, redis, bcmath, gd, mbstring, curl, xml, zip, intl, soap
- **Composer** (latest)
- **Node.js 20** with npm
- **PostgreSQL client** (psql)
- **Git** with enhanced zsh plugins
- **Docker-in-Docker** for running additional containers

### Run Database Migrations

Once the container is ready:
```bash
php artisan migrate
```

### Start Development Servers

```bash
composer dev
```

This starts:
- Laravel dev server on http://localhost:8080
- Vite dev server with hot reload
- Queue worker
- Log viewer (pail)

Or start services individually:
```bash
php artisan serve --host=0.0.0.0 --port=8080
npm run dev
```

## Configuration Files

### `.devcontainer/Dockerfile`
Defines the container image with PHP and all required extensions.

### `.devcontainer/devcontainer.json`
Configures:
- Volume mounts for node_modules and vendor
- Port forwarding (8080)
- VS Code extensions to install
- Initialization and post-create commands

### `.devcontainer/initializeCommand.sh`
Runs on host before container starts:
- Creates Docker network for services

### `.devcontainer/postCreateCommand.sh`
Runs inside container after creation:
- Installs composer dependencies
- Installs npm dependencies
- Creates .env file if needed
- Generates application key

## Useful Aliases

The devcontainer includes helpful aliases:
- `art` → `php artisan`
- `artisan` → `php artisan`
- `test` → `php artisan test`
- `migrate` → `php artisan migrate`

Use them like: `art migrate` instead of `php artisan migrate`

## Troubleshooting

### Container won't build
- Ensure Docker Desktop is running
- Try rebuilding: Command Palette → "Dev Containers: Rebuild Container"

### Permission errors
```bash
sudo chown -R vscode:vscode /home/vscode/project
```

### Port 8080 already in use
Update port in:
1. `.env`: `APP_URL=http://localhost:YOUR_PORT`
2. `.devcontainer/devcontainer.json`: `forwardPorts`
3. Composer dev scripts

## Next Steps
See [03-debug-configuration.md](03-debug-configuration.md) for setting up Xdebug.
