# Debug Configuration

## Why This Step
Setting up Xdebug enables step-by-step debugging of PHP code directly in VSCode. Since PHP runs directly in the devcontainer (not in a separate Sail container), debugging is simpler and more straightforward with no additional container layers.

## What It Does
- Configures Xdebug within the devcontainer
- Sets up VSCode to connect to the Xdebug server
- Establishes proper path mappings for debugging
- Enables debugging, tracing, and code coverage capabilities

## Implementation

### Xdebug is Already Installed
The devcontainer Dockerfile includes Xdebug installation via the `php-xdebug` package, so no additional installation is needed.

### Create VSCode Launch Configuration
The `.vscode/launch.json` file should already exist with the following content:

```json
{
  "version": "0.2.0",
  "configurations": [
      {
          "name": "Listen for Xdebug",
          "type": "php",
          "request": "launch",
          "log": false,
          "port": 9003,
          "pathMappings": {
              "/home/vscode/project": "${workspaceFolder}"
          }
      }
  ]
}
```

The path mapping tells Xdebug that files at `/home/vscode/project` inside the devcontainer correspond to files in your VSCode workspace folder.

### Usage

1. **Set a breakpoint** in your PHP code by clicking in the gutter next to a line number
2. **Start the debugger** in VSCode:
   - Press `F5`, or
   - Go to Run and Debug panel (Ctrl+Shift+D), or
   - Click "Listen for Xdebug" in the debug dropdown
3. **Trigger the code** by visiting your application in the browser or running artisan commands
4. **Debug!** VSCode will pause execution at your breakpoints

### Advantages Over Sail Setup

Running PHP directly in the devcontainer provides several debugging benefits:

- **Simpler configuration**: No need for `SAIL_XDEBUG_*` environment variables
- **Direct connection**: Xdebug runs in the same container as VSCode Server
- **Easier path mapping**: Single path mapping instead of nested container paths
- **Better performance**: No container-to-container communication overhead
- **Consistent environment**: Debugging environment matches your development environment exactly

### Troubleshooting

If debugging doesn't work:

1. **Verify Xdebug is installed**:
   ```bash
   php -v
   # Should show "with Xdebug"
   ```

2. **Check Xdebug configuration**:
   ```bash
   php -i | grep xdebug
   ```

3. **Restart the devcontainer**:
   Command Palette (F1) → "Dev Containers: Rebuild Container"

4. **Check port 9003 is not in use**:
   Make sure no other debugger is using port 9003
