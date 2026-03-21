# VS Code Dev Container Setup

## Overview

This starterkit uses VS Code Dev Containers to provide a fully configured, containerized development environment. Unlike Laravel Sail, PHP runs directly in the devcontainer where your IDE operates, giving you:

- **Faster command execution** - Run `php artisan` directly, no wrapper needed
- **Better IDE integration** - IntelliSense, debugging, and extensions all work seamlessly
- **Consistent environment** - Every developer gets the same setup, no "works on my machine" issues
- **Lower complexity** - One container with everything, not nested containers

### What's Included

The devcontainer comes pre-configured with:

- **PHP 8.x** with extensions: pgsql, redis, bcmath, gd, mbstring, curl, xml, zip, intl, soap
- **Composer** (latest)
- **Node.js 22** with npm
- **PostgreSQL client** (psql)
- **Git** with enhanced zsh plugins
- **noVNC, Xvfb, Fluxbox** for headed browser automation
- **mcp-proxy** for MCP server integration
- **Docker-in-Docker** for running additional containers

## Usage

### Opening the Project

1. Open the project in VS Code
2. Click "Reopen in Container" when prompted, or use Command Palette (F1) → "Dev Containers: Reopen in Container"

The devcontainer automatically installs dependencies and sets up your environment on first open.

### Running the Development Server

```bash
composer dev
```

This starts Laravel dev server, Vite with hot reload, queue worker, and log viewer.

Or start services individually:

```bash
php artisan serve --host=0.0.0.0 --port=8080
npm run dev
```

### Running Migrations

```bash
php artisan migrate
```

### Helpful Aliases

The devcontainer includes these shortcuts:

| Alias | Command |
|-------|---------|
| `art` | `php artisan` |
| `artisan` | `php artisan` |
| `test` | `php artisan test` |
| `migrate` | `php artisan migrate` |

### Rebuilding the Container

If you modify the Dockerfile or devcontainer.json:

Command Palette (F1) → "Dev Containers: Rebuild Container"

## Configuration

### Key Files

| File | Purpose |
|------|---------|
| `.devcontainer/Dockerfile` | Container image with PHP and extensions |
| `.devcontainer/devcontainer.json` | VS Code extensions, port forwarding, volume mounts |
| `.devcontainer/initializeCommand.sh` | Runs on host before container starts (creates Docker network) |
| `.devcontainer/postCreateCommand.sh` | Runs after container creation (installs dependencies, creates .env) |

### Customization

**Adding PHP extensions:**
Edit `.devcontainer/Dockerfile` and add to the `install-php-extensions` command.

**Adding VS Code extensions:**
Edit `.devcontainer/devcontainer.json` under `customizations.vscode.extensions`.

**Changing ports:**
Run `configure-ports.sh` to switch between 3 port presets. This is handled automatically by "Dev: Start", or run manually:

```bash
devtools/setup/configure-ports.sh
```

Three presets avoid port conflicts when running multiple devcontainers:

| Preset | Laravel | Vite | noVNC |
|--------|---------|------|-------|
| Default | 8080 | 5173 | 6080 |
| Preset 2 | 8081 | 5174 | 6081 |
| Preset 3 | 8082 | 5175 | 6082 |

## Troubleshooting

### Container won't build
- Ensure Docker Desktop is running
- Try rebuilding: Command Palette → "Dev Containers: Rebuild Container"

### Permission errors
```bash
sudo chown -R vscode:vscode /home/vscode/project
```

---

**Next:** [Debug Configuration](03-debug-configuration.md) - Set up Xdebug for step-through debugging.