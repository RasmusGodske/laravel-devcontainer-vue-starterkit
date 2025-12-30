# Architecture

This document explains how SubAgentReviewer2 is organized and how the pieces fit together.

## Directory Structure

```
SubAgentReviewer2/
├── main.py                 # Entry point - hook handler
├── config.json             # Configuration
├── hook.log                # Global log file
├── sessions/               # Session data (auto-generated)
└── src/
    ├── __init__.py         # Re-exports all public classes
    ├── Paths.py            # Centralized path management
    ├── loggers/
    │   ├── BaseLogger.py       # Abstract base logger
    │   ├── GlobalLogger.py     # Writes to hook.log
    │   ├── AgentLogger.py      # Writes to agent logs.txt
    │   └── ReviewLogger.py     # Writes to review logs.txt
    ├── models/
    │   ├── Config.py           # ReviewerConfig, ReviewerSettings
    │   ├── HookInput.py        # Parsed hook input
    │   ├── Session.py          # Session, TrackedAgent
    │   ├── TranscriptAnalysis.py
    │   └── transcript/
    │       ├── FileChange.py       # File modification info
    │       ├── ToolCall.py         # Tool call info
    │       └── TranscriptEntry.py  # Single transcript line
    └── services/
        ├── storage/
        │   ├── SessionPathResolver.py  # Resolves session directories
        │   ├── AgentPathResolver.py    # Resolves agent directories
        │   └── SessionStorageService.py
        └── transcript/
            ├── TranscriptParserService.py
            └── TranscriptDiscoveryService.py
```

## Design Principles

### 1. Single Responsibility

Each class has one job:
- **Resolvers** → Find/create directory paths
- **Services** → Business logic (storage, parsing)
- **Models** → Data structures
- **Loggers** → Write logs

### 2. Dependency Injection

Services receive their dependencies through constructors:

```python
# Good: Dependencies passed in
storage = SessionStorageService(sessions_dir=Path("./sessions"))

# Bad: Hard-coded paths
storage = SessionStorageService()  # uses global path internally
```

### 3. Timestamped Directories

All directories use timestamp prefixes for sortability:

```
{timestamp}-{identifier}

Examples:
2025-12-10T17-08-31-abc123           # Session
2025-12-10T17-09-45-backend-engineer-e4d687e4  # Agent
```

This allows `ls` to show chronological order without parsing metadata.

## Core Components

### Paths (`src/Paths.py`)

Centralized path management. Single source of truth for all directory/file locations.

```python
paths = Paths()
paths.sessions_dir       # ./sessions
paths.global_log         # ./hook.log
paths.backend_review_tool  # devtools/backend-review/main.py
```

### Path Resolvers

**SessionPathResolver** - Resolves session directories:

```python
resolver = SessionPathResolver(sessions_dir)

# Find existing session by ID (scans for directories ending with -{id})
path = resolver.find("abc-123")  # Returns None if not found

# Find or create path for session
path = resolver.resolve("abc-123")  # Returns existing or new timestamped path
```

**AgentPathResolver** - Resolves agent directories within a session:

```python
resolver = AgentPathResolver(session_dir)

# Find existing agent
path = resolver.find("e4d687e4")

# Find or create path for agent
path = resolver.resolve("e4d687e4", "backend-engineer")

# Review paths
review_dir = resolver.review_dir("e4d687e4", review_number=1)
log_path = resolver.review_log("e4d687e4", review_number=1)
```

### SessionStorageService

High-level API for session/agent/review storage. Combines resolvers with JSON persistence.

```python
storage = SessionStorageService(sessions_dir)

# Track agent lifecycle
session, agent_dir = storage.track_agent_start(session_id, agent_id, agent_type)
session, agent, agent_dir = storage.track_agent_stop(session_id, agent_id)

# Create review directory
review_dir, review_num = storage.create_review_dir(session_id, agent_id)

# Get paths for review files
paths = storage.get_review_paths(session_id, agent_id, review_number=1)
# Returns: {"dir": Path, "markdown": Path, "file_changes": Path, "log": Path}
```

### Models

**HookInput** - Parses JSON from Claude Code:

```python
hook_input = HookInput.from_dict(raw_json)
hook_input.session_id
hook_input.agent_id
hook_input.agent_type           # Only in SubagentStart
hook_input.agent_transcript_path  # Only in SubagentStop
hook_input.is_start_event
hook_input.is_stop_event
```

**Session** - Tracks agents within a Claude Code session:

```python
session = Session(session_id="abc", started_at="2025-...")
session.add_agent("e4d687e4", "backend-engineer")
session.end_agent("e4d687e4", transcript_path="...")
agent_type = session.get_agent_type("e4d687e4")
```

**TranscriptAnalysis** - Result of parsing an agent transcript:

```python
analysis = parser.parse(transcript_path)
analysis.file_changes      # List[FileChange]
analysis.initial_prompt    # The task given to the agent
analysis.has_php_changes
analysis.has_frontend_changes
analysis.php_files
analysis.frontend_files
```

### Loggers

Three-level logging hierarchy:

```
GlobalLogger (hook.log)
└── AgentLogger (agents/{agent}/logs.txt)
    └── ReviewLogger (agents/{agent}/reviews/{n}/logs.txt)
```

All loggers extend `BaseLogger` which provides:
- File logging with timestamps
- Optional stderr output
- Context manager support (`with logger:`)

```python
# Global logger
global_logger = GlobalLogger(paths)
global_logger.log_hook_start(session_id, event_name)
global_logger.log_hook_end(session_id, decision, duration_ms)

# Agent logger
agent_logger = AgentLogger(agent_dir, agent_id, agent_type)
agent_logger.log_agent_start()
agent_logger.log_file_changes(["file1.php", "file2.php"])

# Review logger
review_logger = ReviewLogger(review_dir, review_number, agent_id)
review_logger.log_review_start(files_to_review)
review_logger.log_decision("allow", "All checks passed")
```

## Data Flow

### SubagentStart

```
1. main.py receives JSON from stdin
2. HookInput.from_dict() parses input
3. SessionStorageService.track_agent_start():
   a. SessionPathResolver.resolve() → session directory
   b. AgentPathResolver.resolve() → agent directory (created)
   c. Session.add_agent() → updates session.json
4. Return "allow" (no output)
```

### SubagentStop

```
1. main.py receives JSON from stdin
2. HookInput.from_dict() parses input
3. Check stop_hook_active (prevent infinite loops)
4. SessionStorageService.track_agent_stop():
   a. Load session.json
   b. Look up agent_type from tracked agents
   c. AgentPathResolver.find() → agent directory
5. ReviewerConfig.should_review_agent() → check if agent type needs review
6. TranscriptParserService.parse() → extract file changes
7. (TODO) Run reviewer based on file types
8. (TODO) If issues found, output block JSON
```

## File Formats

### session.json

```json
{
  "session_id": "abc-123",
  "started_at": "2025-12-10T17:08:31.781114",
  "transcript_path": "/home/.../.claude/projects/.../abc-123.jsonl",
  "agents": {
    "e4d687e4": {
      "agent_id": "e4d687e4",
      "agent_type": "backend-engineer",
      "started_at": "2025-12-10T17:08:31.781119",
      "ended_at": "2025-12-10T17:10:15.680263",
      "transcript_path": "/home/.../.claude/projects/.../agent-e4d687e4.jsonl",
      "reviewed": true,
      "review_decision": "allow"
    }
  }
}
```

### config.json

```json
{
  "agents_to_review": ["backend-engineer", "frontend-engineer"],
  "settings": {
    "skip_if_no_file_changes": true,
    "max_review_cycles": 3
  }
}
```

## Extending

### Adding a new agent type to review

1. Add to `config.json`:
   ```json
   {"agents_to_review": ["backend-engineer", "frontend-engineer", "my-new-agent"]}
   ```

2. Create reviewer tool at `devtools/my-new-review/main.py`

3. Update file categorization in `FileChange.py` if needed

### Adding new file types

Edit `src/models/transcript/FileChange.py`:

```python
@property
def is_my_type(self) -> bool:
    return self.extension in ("ext1", "ext2")
```

### Adding new log events

Extend the appropriate logger class:

```python
class AgentLogger(BaseLogger):
    def log_my_event(self, data: str) -> None:
        self.info(f"My event: {data}")
```

## Testing

```bash
# Run all tests
uv run pytest

# Test with verbose output
uv run pytest -v

# Test specific module
uv run pytest tests/test_session_storage.py
```

## Future Work

- [ ] Implement ReviewerService (calls backend-review/frontend-review)
- [ ] Add file-changes.json output
- [ ] Add review.md generation
- [ ] Add metrics/statistics collection
- [ ] Add session cleanup command
