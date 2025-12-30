# Devtools

## Why This Step
Development tools and scripts that improve the developer experience, particularly for AI-assisted development with Claude Code. These are ported from the main Prowi project and adapted for the starterkit.

## What It Does
- Provides helper scripts for environment setup and dependency management
- Adds automatic code review for Claude Code subagents via hooks
- Includes a standalone AI-powered code reviewer CLI

## Directory Structure

```
devtools/
├── claude-hooks/
│   └── SubAgentReviewer/     # Hook that reviews subagent code changes
├── code-reviewer/            # Standalone AI code review CLI
├── ensure-*.sh               # Environment setup scripts
├── serve.sh                  # PHP server wrapper with restart handling
├── configure-urls.sh         # URL configuration for Codespaces
└── pyproject.toml            # Python dependencies (uses uv)
```

## Key Components

### Claude Code Hooks

The `SubAgentReviewer` automatically reviews code changes made by Claude Code subagents (like `backend-engineer` or `frontend-engineer`) before they complete. If issues are found, the subagent is blocked and given feedback to fix.

Configured in `.claude/settings.json`:
```json
{
  "hooks": {
    "SubagentStart": [...],
    "SubagentStop": [...]
  }
}
```

### Code Reviewer CLI

A standalone tool for AI-powered code reviews using Claude Agent SDK. Used by the SubAgentReviewer hook but can also be run manually:

```bash
cd devtools/code-reviewer
uv run python cli.py --files "app/Models/User.php"
```

### Helper Scripts

| Script | Purpose |
|--------|---------|
| `ensure-env.sh` | Creates `.env` from `.env.example` if missing |
| `ensure-composer.sh` | Installs/updates Composer dependencies |
| `ensure-npm.sh` | Installs/updates npm dependencies |
| `ensure-app-key.sh` | Generates `APP_KEY` if not set |
| `ensure-migrated.sh` | Waits for DB, runs migrations and seeds |
| `configure-urls.sh` | Configures URLs for Codespaces vs local |
| `serve.sh` | PHP server wrapper with graceful restart |

## Dependencies

Uses `uv` for Python package management. The devtools depend on:
- `claude-agent-sdk` - For AI-powered reviews

Install with:
```bash
cd devtools
uv sync
```
