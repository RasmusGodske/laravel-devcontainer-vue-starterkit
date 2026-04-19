# Playwright MCP Server

A multi-session wrapper around `@playwright/mcp` that lets multiple agents drive browsers in parallel without interfering with each other.

## Server

| Server | Config Key | Purpose |
|--------|-----------|---------|
| **Playwright** | `playwright` | Vanilla Playwright tools with multi-session support |

## Files

```
playwright/
  lib/
    session-manager.cjs       # Multi-session management, tool proxying, server bootstrap
  playwright-server.cjs       # Server entry point (thin bootstrap)
  playwright.sh               # Launcher
```

## Multi-Session Support

Each call can include a `session_id` to target an isolated browser context. Without it, a `"default"` session is used, so single-agent usage works with no changes.

```
create_session          -> returns session-1
browser_navigate(url, session_id: "session-1")
close_session(session_id: "session-1")
```

This matters because parallel agents sharing one tab would compete for navigation, causing chaos.

## Headed vs Headless

The launcher chooses based on whether the desktop service is running:

- **Desktop running** (`/tmp/.X1-lock` exists): headed mode, Chromium renders on `DISPLAY=:1`, visible via noVNC at `http://localhost:$NOVNC_PORT`.
- **Desktop stopped**: fully headless.

Start the desktop with `service:desktop start` to see what the agent sees.

## Shared Library (`lib/session-manager.cjs`)

Exports:

| Export | Purpose |
|--------|---------|
| `startServer(options)` | Bootstrap helper — config, factory, watchdog, MCP server start |
| `PlaywrightSessionManager` | Multi-session backend class (context map, tool proxying, session_id injection) |
| `z` | Zod (re-exported from Playwright's bundle, for custom tool schemas) |
| `pw` | Module resolver for `@playwright/mcp` internals |

### Extension points

Consumers customize behavior via `startServer()` options:

- **`onContextCreated(context, sessionId)`** — hook into browser context creation (e.g., inject headers)
- **`customTools: [{ definition, handler }]`** — register additional MCP tools; handler receives `(args, sessionManager)`

### Adding a new server

```javascript
const { startServer, z } = require('./lib/session-manager.cjs');

startServer({
  name: 'My Server',
  nameInConfig: 'my-server',
  version: '0.1.0',
  // Optional:
  onContextCreated: (context, sessionId) => { /* patch context */ },
  customTools: [{
    definition: { name: 'my_tool', description: '...', inputSchema: z.toJSONSchema(z.object({ ... })) },
    handler: async (args, sessionManager) => {
      const context = sessionManager.getContext(args.session_id || 'default');
      // ... use context
      return { content: [{ type: 'text', text: '### Result\n...' }] };
    },
  }],
});
```

## Launcher

`playwright.sh` handles the bootstrap:

1. Detect headed/headless mode (check for Xvfb via `/tmp/.X1-lock`)
2. Ensure `@playwright/mcp@0.0.68` is available (global install preferred, npx cache fallback, bootstrap as last resort)
3. Resolve the module path and export `PLAYWRIGHT_MCP_NODE_MODULES`
4. Set output directory to `.playwright-mcp/`
5. `exec node` the server
