#!/usr/bin/env python3
"""
Telemetry Sync CLI.

Sync devtools telemetry data to a shared branch for cross-developer analysis.

Usage:
    ./cli.py setup              # First-time setup (create branch + worktree)
    ./cli.py sync               # Sync local telemetry to branch
    ./cli.py sync -m "message"  # Sync with custom commit message
    ./cli.py status             # Show sync status
"""

import argparse
import sys
from pathlib import Path

from src.config import load_config
from src.services import GitService, SyncService

CLI_DIR = Path(__file__).parent.resolve()
CONFIG_PATH = CLI_DIR / "config.json"


def get_project_root() -> Path:
    """Get project root directory."""
    # CLI_DIR -> devtools -> project_root
    return CLI_DIR.parent.parent


def create_services() -> SyncService:
    """Create configured sync service."""
    project_root = get_project_root()
    config = load_config(CONFIG_PATH, project_root)
    git = GitService(project_root)
    return SyncService(config, git)


def cmd_setup(args: argparse.Namespace) -> int:
    """Handle setup command."""
    service = create_services()
    result = service.setup()

    if result.success:
        print(f"[OK] {result.message}")
        return 0
    else:
        print(f"[ERROR] {result.message}", file=sys.stderr)
        return 1


def cmd_sync(args: argparse.Namespace) -> int:
    """Handle sync command."""
    service = create_services()
    result = service.sync(message=args.message)

    if result.success:
        if result.files_synced > 0:
            print(f"[OK] {result.message}")
            if result.commit_hash:
                print(f"     Commit: {result.commit_hash[:8]}")
        else:
            print(f"[OK] {result.message}")
        return 0
    else:
        print(f"[ERROR] {result.message}", file=sys.stderr)
        return 1


def cmd_status(args: argparse.Namespace) -> int:
    """Handle status command."""
    service = create_services()
    status = service.status()

    print("Telemetry Sync Status")
    print("=" * 40)
    print(f"Branch exists:   {'Yes' if status.branch_exists else 'No'}")
    print(f"Worktree exists: {'Yes' if status.worktree_exists else 'No'}")
    print(f"Setup complete:  {'Yes' if status.is_setup else 'No'}")
    print()
    print(f"Pending files:   {status.pending_count}")

    if status.pending_files and not args.quiet:
        print()
        print("Files to sync:")
        for f in status.pending_files[:20]:  # Limit display
            print(f"  - {f}")
        if len(status.pending_files) > 20:
            print(f"  ... and {len(status.pending_files) - 20} more")

    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Sync devtools telemetry to shared branch",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # setup command
    setup_parser = subparsers.add_parser(
        "setup",
        help="First-time setup (create branch and worktree)",
    )
    setup_parser.set_defaults(func=cmd_setup)

    # sync command
    sync_parser = subparsers.add_parser(
        "sync",
        help="Sync local telemetry to shared branch",
    )
    sync_parser.add_argument(
        "-m", "--message",
        help="Custom commit message (auto-generated if not provided)",
    )
    sync_parser.set_defaults(func=cmd_sync)

    # status command
    status_parser = subparsers.add_parser(
        "status",
        help="Show sync status and pending files",
    )
    status_parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Don't list individual files",
    )
    status_parser.set_defaults(func=cmd_status)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
