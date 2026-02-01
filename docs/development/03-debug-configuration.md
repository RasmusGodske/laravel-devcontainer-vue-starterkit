# Debug Configuration

## Overview

Step-through debugging lets you pause PHP execution, inspect variables, and trace code flow directly in VSCode. Since PHP runs in the devcontainer (not a separate Sail container), debugging is simpler with no extra container layers or complex path mappings.

Xdebug is pre-configured and ready to use - just set breakpoints and start debugging.

## Usage

### Starting a Debug Session

1. **Set a breakpoint** - Click in the gutter next to a line number in any PHP file
2. **Start the debugger** - Use one of these methods:
   - Press `F5`
   - Open Run and Debug panel (`Ctrl+Shift+D`) and click the play button
   - Select "Listen for Xdebug" from the debug dropdown
3. **Trigger your code** - Visit your app in the browser or run an artisan command
4. **Debug** - VSCode pauses at your breakpoints, letting you inspect variables and step through code

### Debugging Artisan Commands

```bash
php artisan your:command
```

With the debugger listening, breakpoints in your command will be hit automatically.

### Debugging Web Requests

Simply visit any page in your browser while the debugger is listening. Breakpoints in controllers, middleware, and services will pause execution.

## Configuration

### Key Files

| File | Purpose |
|------|---------|
| `.vscode/launch.json` | VSCode debugger configuration |
| `.devcontainer/Dockerfile` | Xdebug PHP settings (lines 17-21) |

### Xdebug Settings

The devcontainer configures Xdebug with these defaults:

| Setting | Value | Purpose |
|---------|-------|---------|
| `xdebug.mode` | `debug` | Enables step debugging |
| `xdebug.start_with_request` | `yes` | Auto-starts debugging for every request |
| `xdebug.client_host` | `127.0.0.1` | Connects to local VSCode |
| `xdebug.client_port` | `9003` | Default Xdebug port |

### Customization

To modify Xdebug behavior, edit the Dockerfile and rebuild the container:

```bash
# After editing .devcontainer/Dockerfile
# Command Palette (F1) → "Dev Containers: Rebuild Container"
```

Common customizations:
- Change `xdebug.mode=debug,coverage` to enable code coverage
- Set `xdebug.start_with_request=trigger` to only debug when explicitly triggered

### Troubleshooting

If breakpoints are not being hit:

1. **Verify Xdebug is installed**: `php -v` should show "with Xdebug"
2. **Check the debugger is listening**: Look for the orange debug toolbar in VSCode
3. **Rebuild the container**: Command Palette → "Dev Containers: Rebuild Container"
4. **Ensure port 9003 is free**: No other process should be using this port