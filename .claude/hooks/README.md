# Claude Code Hooks

This directory contains hooks that automatically run during Claude Code sessions to maintain code quality.

## Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         SESSION START                           │
│                      session-start.py                           │
│                   (logs available tools)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AFTER EACH WRITE/EDIT                        │
│                       after-write.py                            │
│                                                                 │
│  1. Track file in .claude/sessions/{session_id}.json            │
│  2. PHP only: run `php -l` syntax check                         │
│     - Exit 2 on syntax error → Claude fixes it                  │
│                                                                 │
│  (Formatting deferred to avoid removing unused imports)         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      END OF TURN (Stop)                         │
│                    end-of-turn-check.py                         │
│                                                                 │
│  Reads session tracker, then for files modified THIS session:   │
│                                                                 │
│  PHP files:                                                     │
│    1. Pint (format modified files)                              │
│    2. PHPStan (entire project - catches cascading issues)       │
│                                                                 │
│  JS/TS/Vue files:                                               │
│    1. ESLint --fix                                              │
│                                                                 │
│  On errors → JSON "block" with reason (Claude sees & fixes)     │
│  On success → Clear session tracker                             │
└─────────────────────────────────────────────────────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `session-start.py` | Logs available tools at session start |
| `after-write.py` | Tracks files + fast PHP syntax check |
| `end-of-turn-check.py` | Runs formatters and linters on session files |
| `session_tracker.py` | Utility to track files per session |
| `hook_logger.py` | Shared logging utility |
| `hooks.log` | Log file (gitignored) |

## Session Tracking

Each session gets its own directory at `.claude/sessions/{session_id}/`:

```
.claude/sessions/
  abc123.../
    files.json    # List of modified files
    hooks.log     # Log file for this session
```

This ensures:
- Only files from the current session are checked (not other concurrent sessions)
- End-of-turn checks target exactly what Claude modified
- Logs are easy to debug per session
- Session directory is cleared after successful checks

## JSON Output

Hooks use JSON output to provide feedback to Claude:

```json
{
  "decision": "block",
  "reason": "PHPStan errors:\n..."
}
```

- `decision: "block"` - Tells Claude there's an issue to fix
- `reason` - The error message Claude sees and can act on

This is gentler than exit code 2 - Claude gets structured feedback and can decide how to proceed.

## Logging

Each session logs to `.claude/sessions/{session_id}/hooks.log`:

```
[2025-12-07 00:05:00] [INFO] [end-of-turn] [START] PHPStan on entire project
[2025-12-07 00:05:45] [SUCCESS] [end-of-turn] [DONE] PHPStan passed
```

Format: `[timestamp] [level] [hook_name] message`

- `[START]`/`[DONE]` markers show command progress
- Each session has its own log for easy debugging
- Session directory is cleaned up after successful checks

## Configuration

Hooks are configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      { "matcher": "*", "hooks": [{ "type": "command", "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/session-start.py" }] }
    ],
    "PostToolUse": [
      { "matcher": "Write|Edit", "hooks": [{ "type": "command", "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/after-write.py" }] }
    ],
    "Stop": [
      { "matcher": "*", "hooks": [{ "type": "command", "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/end-of-turn-check.py" }] }
    ]
  }
}
```

## Why Deferred Formatting?

Formatting (Pint) is run at end-of-turn rather than after each write because:

1. Claude might add an import in one edit
2. Then use it in a subsequent edit
3. If Pint ran immediately, it would remove the "unused" import before Claude uses it

By deferring to end-of-turn, all edits are complete and imports are properly used.
