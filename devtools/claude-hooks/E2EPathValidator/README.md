# E2EPathValidator

Pre-tool hook that validates E2E test file paths using Claude Agent SDK.

## The Problem

E2E test directories often need to follow specific conventions (e.g., mirroring the pages/views structure). Developers and AI agents may accidentally create tests in the wrong location, following URL routes instead of the actual file structure.

## The Solution

This hook intercepts `Write` and `Edit` tool calls for E2E test files and uses Claude Agent SDK to validate the path against the project's conventions.

**Key benefits:**
- **Flexible** - Claude reads your project's rules, not hardcoded logic
- **Project-agnostic** - Works with any project that has E2E conventions defined
- **Helpful feedback** - Provides the correct path when blocking
- **Programmatic** - Uses Claude Agent SDK for reliable, structured interaction

## How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Claude calls    │────▶│ PreToolUse hook  │────▶│ Is E2E test?    │
│ Write/Edit tool │     │ fires            │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                        │
                              ┌─────────────────────────┘
                              ▼
                       ┌──────────────────┐
                  NO   │ Allow operation  │
             ┌────────▶│                  │
             │         └──────────────────┘
             │
      ┌──────┴───────┐
      │ YES          │
      ▼              │
┌──────────────────┐ │
│ Run Claude Agent │ │
│ SDK validation   │ │
└──────────────────┘ │
      │              │
      ▼              │
┌──────────────────┐ │     ┌──────────────────┐
│ Agent reads      │ │     │ Block with       │
│ project rules    │─┼────▶│ helpful message  │
│ and validates    │ │     └──────────────────┘
└──────────────────┘ │            ▲
      │              │            │ BLOCK
      │ ALLOW        │            │
      └──────────────┴────────────┘
```

## Project Structure

```
E2EPathValidator/
├── main.py              # Hook entry point
├── prompt.md            # Prompt template for validation
├── pyproject.toml       # Dependencies
├── README.md            # This file
└── src/
    ├── __init__.py
    ├── models/
    │   ├── __init__.py
    │   └── E2EPathValidationResult.py
    └── services/
        ├── __init__.py
        └── E2EPathValidatorService.py
```

## Configuration

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "cd $CLAUDE_PROJECT_DIR/devtools/claude-hooks/E2EPathValidator && uv run python main.py",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

**Note:** Timeout is set to 120 seconds to allow the Claude agent time to read rules and validate.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `E2E_TEST_PATTERN` | `e2e/tests/` | Pattern to identify E2E test files |
| `CLAUDE_PROJECT_DIR` | (auto-detected) | Project root directory |
| `E2E_VALIDATOR_VERBOSE` | `false` | Enable verbose logging to stderr |

## How Claude Validates

When triggered, the hook uses Claude Agent SDK to:

1. Read the project's E2E test conventions from `.claude/rules/`
2. Check if the corresponding page/view file exists
3. Return `<decision>allow</decision>` or `<decision>block</decision><reason>...</reason>`

The agent has access to `Read`, `Glob`, and `Grep` tools to explore the project.

## Example Output

When Claude blocks an invalid path:

```json
{
  "decision": "block",
  "reason": "The test path `e2e/tests/Feature/Settings/Users/Index/smoke.spec.ts` is incorrect.\n\n**Problem:** There is no page at `resources/js/Pages/Feature/Settings/Users/Index.vue`\n\n**Actual page location:** `resources/js/Pages/Feature/Users/Index.vue`\n\n**Correct test path:** `e2e/tests/Feature/Users/Index/smoke.spec.ts`"
}
```

## Requirements

- Python 3.10+
- Claude Agent SDK (`pip install claude-agent-sdk` or use `uv`)
- E2E test conventions defined in `.claude/rules/`

## Testing Manually

```bash
cd /path/to/project

# Test with an E2E test path (Claude will validate)
echo '{
  "tool": "Write",
  "input": {
    "file_path": "e2e/tests/Feature/Example/smoke.spec.ts"
  }
}' | cd devtools/claude-hooks/E2EPathValidator && uv run python main.py

# Test with a non-E2E file (should allow immediately)
echo '{
  "tool": "Write",
  "input": {
    "file_path": "src/services/UserService.ts"
  }
}' | cd devtools/claude-hooks/E2EPathValidator && uv run python main.py

# Enable verbose mode for debugging
E2E_VALIDATOR_VERBOSE=1 echo '...' | cd devtools/claude-hooks/E2EPathValidator && uv run python main.py
```

## Graceful Degradation

The hook is designed to fail open (allow) in error cases:
- If Claude Agent SDK fails
- If the agent times out
- If response format is unexpected

This ensures the hook never blocks development due to technical issues.

## Customizing the Prompt

Edit `prompt.md` to customize:
- What conventions to check
- How to format error messages
- What files to look for

The prompt uses `{file_path}` as a placeholder for the path being validated.
