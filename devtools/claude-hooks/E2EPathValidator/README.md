# E2EPathValidator

Pre-tool hook that validates E2E route test file paths using Claude Agent SDK.

## The Problem

E2E route tests must:
1. Be placed in `e2e/tests/routes/`
2. Have directory names that **exactly match** Laravel route segments
3. Correspond to an actual Laravel route

Developers and AI agents may accidentally create tests for non-existent routes or use incorrect directory naming.

## The Solution

This hook intercepts `Write` and `Edit` tool calls for E2E test files in `e2e/tests/routes/` and uses Claude Agent SDK to:
1. Check if the route actually exists via `php artisan route:list`
2. Validate directory names exactly match Laravel route segments
3. Provide helpful feedback with the correct path when blocking

**Key benefits:**
- **Route validation** - Verifies the route exists before allowing test creation
- **Exact matching** - Ensures directory names match Laravel routes exactly
- **Helpful feedback** - Shows the correct path or available routes when blocking
- **Scoped** - Only validates files in `e2e/tests/routes/`, ignores other test types

## How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│ Claude calls    │────▶│ PreToolUse hook  │────▶│ In e2e/tests/routes?│
│ Write/Edit tool │     │ fires            │     │                     │
└─────────────────┘     └──────────────────┘     └─────────────────────┘
                                                       │
                             ┌─────────────────────────┘
                             ▼
                      ┌──────────────────┐
                 NO   │ Allow operation  │
            ┌────────▶│ (not a route test)│
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
│ Agent runs:      │ │     │ Block with       │
│ 1. route:list    │─┼────▶│ helpful message  │
│ 2. Check naming  │ │     └──────────────────┘
└──────────────────┘ │            ▲
     │              │            │ BLOCK (route missing
     │ ALLOW        │            │ or bad naming)
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

When triggered for files in `e2e/tests/routes/`, the hook uses Claude Agent SDK to:

1. Extract the expected Laravel route from the test path
2. Run `php artisan route:list` to verify the route exists
3. Check that all directory names match route segments exactly
4. Return `<decision>allow</decision>` or `<decision>block</decision><reason>...</reason>`

The agent has access to `Read`, `Glob`, `Grep`, and `Bash` tools.

## Example Output

When Claude blocks a non-existent route:

```json
{
  "decision": "block",
  "reason": "The route for test path `e2e/tests/routes/app/non_existent/index/smoke.spec.ts` does not exist.\n\n**Expected route:** `GET /app/non_existent`\n\n**Suggestion:** Run `php artisan route:list --method=GET` to find available routes."
}
```

When Claude blocks mismatched directory names:

```json
{
  "decision": "block",
  "reason": "The test path `e2e/tests/routes/app/commission-plans/index/smoke.spec.ts` does not match the Laravel route.\n\n**Problem:** Directory `commission-plans` should be `commission_plans` to match route `/app/commission_plans`.\n\n**Correct path:** `e2e/tests/routes/app/commission_plans/index/smoke.spec.ts`"
}
```

## Requirements

- Python 3.10+
- Claude Agent SDK (`pip install claude-agent-sdk` or use `uv`)
- E2E test conventions defined in `.claude/rules/`

## Testing Manually

```bash
cd /path/to/project

# Test with a route test path (Claude will validate)
echo '{
  "tool": "Write",
  "input": {
    "file_path": "e2e/tests/routes/app/users/index/smoke.spec.ts"
  }
}' | cd devtools/claude-hooks/E2EPathValidator && uv run python main.py

# Test with a non-route E2E file (should allow immediately)
echo '{
  "tool": "Write",
  "input": {
    "file_path": "e2e/tests/components/Button.spec.ts"
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
- What routes to validate

The prompt uses `{file_path}` as a placeholder for the path being validated.
