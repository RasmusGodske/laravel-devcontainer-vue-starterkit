# SubAgentReviewer2

Automatically reviews code changes made by Claude Code subagents before they complete.

## The Problem

Claude Code agents don't consistently follow project conventions defined in `.claude/rules/`. Even with detailed rules, agents may:
- Skip linting or type-checking
- Ignore naming conventions
- Miss architectural patterns
- Forget to run tests

Telling Claude to "review your code" in CLAUDE.md doesn't work reliably - the agent often forgets or skips the review step.

## The Solution

**SubAgentReviewer2** hooks into Claude Code's lifecycle events to automatically review code:

1. **SubagentStart** - Tracks which agent started (e.g., `backend-engineer`)
2. **SubagentStop** - Intercepts completion, reviews file changes, blocks if issues found

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Claude spawns   │────▶│ SubagentStart    │────▶│ Track agent     │
│ backend-engineer│     │ hook fires       │     │ type & ID       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Agent finishes  │────▶│ SubagentStop     │────▶│ Parse transcript│
│ editing files   │     │ hook fires       │     │ find changes    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Run reviewer    │────▶│ Issues found?    │────▶│ Block agent     │
│ (backend/frontend)    │                  │     │ with feedback   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Key Benefit

Review feedback goes **directly to the subagent**, not the parent. This:
- Preserves the orchestrator's context window
- Lets subagents fix issues autonomously
- Supports multiple review cycles without human intervention

## Quick Start

### 1. Configure the hook in `.claude/settings.json`:

```json
{
  "hooks": {
    "SubagentStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cd $CLAUDE_PROJECT_DIR/devtools/claude-hooks/SubAgentReviewer2 && uv run python main.py",
            "timeout": 30
          }
        ]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cd $CLAUDE_PROJECT_DIR/devtools/claude-hooks/SubAgentReviewer2 && uv run python main.py",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

### 2. Configure which agents to review in `config.json`:

```json
{
  "agents_to_review": [
    "backend-engineer",
    "frontend-engineer"
  ],
  "settings": {
    "skip_if_no_file_changes": true,
    "max_review_cycles": 3
  }
}
```

### 3. That's it!

When `backend-engineer` or `frontend-engineer` subagents stop, they'll be reviewed automatically.

## How It Works

### Hook Input

Claude Code sends JSON via stdin:

**SubagentStart:**
```json
{
  "session_id": "abc-123",
  "hook_event_name": "SubagentStart",
  "agent_id": "e4d687e4",
  "agent_type": "backend-engineer",
  "transcript_path": "~/.claude/projects/.../session.jsonl"
}
```

**SubagentStop:**
```json
{
  "session_id": "abc-123",
  "hook_event_name": "SubagentStop",
  "agent_id": "e4d687e4",
  "agent_transcript_path": "~/.claude/projects/.../agent-e4d687e4.jsonl",
  "stop_hook_active": false
}
```

### Hook Output

To block a subagent, output JSON to stdout:

```json
{
  "decision": "block",
  "reason": "Code review found issues:\n\n- Missing type hints in UserService.php\n- ..."
}
```

To allow (or do nothing), exit with code 0 and no JSON output.

### Review Flow

1. **SubagentStart** → Store `agent_id` → `agent_type` mapping
2. **SubagentStop** → Look up agent type
3. Check if agent type is in `agents_to_review`
4. Parse agent transcript for file changes (Edit, Write, Serena tools)
5. Categorize files (PHP → backend, Vue/TS → frontend)
6. Run appropriate reviewer (`backend-review` or `frontend-review`)
7. Block with feedback if issues found

### Infinite Loop Prevention

The hook checks `stop_hook_active` to prevent loops:
- If `true`, the hook allows immediately (a review agent is completing)
- If `false`, normal review process runs

## Configuration

### config.json

| Option | Type | Description |
|--------|------|-------------|
| `agents_to_review` | `string[]` | Agent types to review (e.g., `["backend-engineer"]`) |
| `settings.skip_if_no_file_changes` | `bool` | Skip review if no files were modified |
| `settings.max_review_cycles` | `int` | Max times to block same agent (prevents infinite loops) |

## Session Storage

Reviews are stored in a structured, sortable hierarchy:

```
sessions/
└── 2025-12-10T17-08-31-{session_id}/
    ├── session.json
    └── agents/
        └── 2025-12-10T17-09-45-backend-engineer-{agent_id}/
            ├── logs.txt
            └── reviews/
                └── 1/
                    ├── review.md
                    ├── file-changes.json
                    └── logs.txt
```

Timestamps prefix directories for chronological sorting.

## Logging

Three levels of logging for transparency:

| Logger | File | Purpose |
|--------|------|---------|
| GlobalLogger | `hook.log` | Hook lifecycle, errors |
| AgentLogger | `agents/{agent}/logs.txt` | Agent events, file changes |
| ReviewLogger | `agents/{agent}/reviews/{n}/logs.txt` | Review execution details |

Enable verbose logging:
```bash
DEBUG=1 echo '{"session_id":"test",...}' | python main.py
```

## Reviewers

The actual review logic lives in separate tools:

- `devtools/backend-review/main.py` - PHP/Laravel review
- `devtools/frontend-review/main.py` - Vue/TypeScript review

These are Claude Agent SDK agents with access to:
- Project rules from `.claude/rules/`
- Linting tools (Pint, ESLint, TypeScript)
- File reading capabilities

## Development

### Prerequisites

- Python 3.10+
- uv (Python package manager)

### Install dependencies

```bash
cd devtools/claude-hooks/SubAgentReviewer2
uv sync
```

### Run tests

```bash
uv run pytest
```

### Test hook manually

```bash
echo '{
  "session_id": "test-123",
  "hook_event_name": "SubagentStop",
  "agent_id": "abc",
  "stop_hook_active": false
}' | uv run python main.py
```

## Cleanup

Old sessions are automatically cleaned up:
- Max age: 7 days
- Max sessions: 100

Cleanup runs after each review.
