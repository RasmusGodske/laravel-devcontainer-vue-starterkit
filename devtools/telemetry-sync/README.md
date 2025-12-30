# Telemetry Sync

Sync devtools telemetry data to a shared branch for cross-developer analysis.

## Overview

This tool syncs local telemetry from `devtools-telemetry/` to a dedicated `devtools-telemetry` branch using git worktrees. This allows developers to share telemetry data without cluttering feature branches.

## Quick Start

```bash
# First-time setup (creates branch + worktree)
./devtools/telemetry-sync/cli.py setup

# Sync your local telemetry
./devtools/telemetry-sync/cli.py sync

# Check status
./devtools/telemetry-sync/cli.py status
```

## Commands

### `setup`

Creates the telemetry branch and worktree. Run once per developer.

```bash
./devtools/telemetry-sync/cli.py setup
```

This will:
1. Create `devtools-telemetry` branch (if it doesn't exist)
2. Create worktree at `../project-telemetry/`

### `sync`

Copies local telemetry to the worktree, commits, and pushes.

```bash
# Auto-generated commit message
./devtools/telemetry-sync/cli.py sync

# Custom commit message
./devtools/telemetry-sync/cli.py sync -m "Add code review sessions"
```

### `status`

Shows setup status and pending files.

```bash
./devtools/telemetry-sync/cli.py status

# Quiet mode (no file list)
./devtools/telemetry-sync/cli.py status -q
```

## Configuration

Edit `config.json` to customize:

```json
{
  "branch_name": "devtools-telemetry",
  "source_dir": "devtools-telemetry",
  "worktree_dir": "project-telemetry"
}
```

| Option | Default | Description |
|--------|---------|-------------|
| `branch_name` | `devtools-telemetry` | Git branch for telemetry |
| `source_dir` | `devtools-telemetry` | Local telemetry directory (relative to project root) |
| `worktree_dir` | `project-telemetry` | Worktree directory (sibling to project) |

## How It Works

```
./devtools-telemetry/          # Local telemetry (gitignored)
    └── code-reviewer/
        └── sessions/
            └── {timestamp}-{id}/
                └── session.json

    ↓ sync ↓

../project-telemetry/          # Git worktree (devtools-telemetry branch)
    └── code-reviewer/
        └── sessions/
            └── {timestamp}-{id}/
                └── session.json
```

1. **Local storage**: Devtools write telemetry to `devtools-telemetry/`
2. **Gitignored**: Data stays local on feature branches
3. **Sync**: This tool copies to worktree and pushes to shared branch
4. **Analysis**: Query the branch to analyze patterns across developers

## Workflow

```bash
# Developer works on feature branch
git checkout feature/my-feature

# Devtools generate telemetry locally
# (code-reviewer, SubAgentReviewer, etc.)

# Periodically sync telemetry
./devtools/telemetry-sync/cli.py sync

# Data is now on devtools-telemetry branch
# Other developers can pull and analyze
```

## Troubleshooting

### "Not set up. Run 'setup' first."

Run the setup command:
```bash
./devtools/telemetry-sync/cli.py setup
```

### Worktree conflicts

If the worktree gets corrupted:
```bash
# Remove worktree
git worktree remove ../project-telemetry

# Re-run setup
./devtools/telemetry-sync/cli.py setup
```

### Push fails

Check if you have push access to the remote:
```bash
cd ../project-telemetry
git push -v
```
