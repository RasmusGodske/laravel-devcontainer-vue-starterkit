# Code Reviewer

A standalone CLI tool for AI-powered code reviews using Claude Agent SDK.

## Features

- **Session Management**: Each review session has a unique ID and log directory
- **Extensible Logging**: Session-scoped logs for debugging and auditing
- **Simple Output**: Returns `{"passed": bool, "feedback": str}` for easy integration
- **Standalone**: No external dependencies on other devtools packages

## Usage

### Basic Review

```bash
./cli.py --files "app/Models/User.php"
```

### With Task Context

```bash
./cli.py --files "app/Models/User.php, app/Services/UserService.php" \
         --task "Added user registration feature"
```

### Custom Session ID

```bash
./cli.py --files "app/Models/User.php" --session my-custom-session
```

### JSON Output

```bash
./cli.py --files "app/Models/User.php" --json
# Output: {"passed": true, "feedback": ""}
```

### Save to File

```bash
./cli.py --files "app/Models/User.php" --output ./review-result.json
```

### Verbose Mode

```bash
./cli.py --files "app/Models/User.php" --verbose
```

## CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--files` | `-f` | Files to review (required, comma-separated) |
| `--task` | `-t` | Description of the task being done (context) |
| `--session` | `-s` | Session ID (auto-generated if not provided) |
| `--output` | `-o` | Save result as JSON to this path |
| `--json` | | Output result as JSON to stdout |
| `--quiet` | `-q` | Only output on failure |
| `--verbose` | `-v` | Enable verbose logging to stderr |

## Serena MCP Integration

The code reviewer uses [Serena](https://github.com/oraios/serena) MCP server for semantic code analysis:

- `find_symbol` - Find classes, methods, functions by name
- `get_symbols_overview` - Get overview of file structure
- `find_referencing_symbols` - Find where code is used
- `search_for_pattern` - Search for patterns in code
- `list_dir` / `find_file` - Directory and file operations

## Session Logging

Each review creates a session directory with logs:

```
sessions/
└── review-20251210-a1b2c3/
    ├── log.txt          # Session log
    └── session.json     # Session metadata
```

Session IDs follow the format: `review-YYYYMMDD-XXXXXX`

## Exit Codes

- `0` - Review passed (no blocking issues)
- `1` - Review blocked (issues found)
- `2` - Error (configuration or runtime error)

## Integration with SubAgentReviewer

This CLI is called by the SubAgentReviewer hook to review subagent code changes:

```python
from pathlib import Path

# SubAgentReviewer calls this CLI via subprocess
result = subprocess.run([
    sys.executable,
    str(Path("devtools/code-reviewer/cli.py")),
    "--files", "app/Models/User.php",
    "--json",
], capture_output=True, text=True)

data = json.loads(result.stdout)
if not data["passed"]:
    # Block with feedback
    print(data["feedback"])
```

## Architecture

```
code-reviewer/
├── cli.py                        # Ultra-slim CLI entry point
├── prompt.md                     # Review prompt template
├── sessions/                     # Session logs (gitignored)
└── src/
    ├── models/
    │   ├── CodeReviewResult.py   # Review result dataclass
    │   ├── CodeReviewOptions.py  # Configuration options
    │   └── CodeReviewSession.py  # Session tracking
    ├── services/
    │   ├── CodeReviewService.py  # Main review logic (Claude Agent SDK)
    │   └── CodeReviewSessionManager.py  # Session/UUID management
    └── loggers/
        └── CodeReviewLogger.py   # Session-scoped file logger
```

## Dependencies

- Python 3.10+
- `claude_agent_sdk` - For AI-powered reviews
