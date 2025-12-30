#!/usr/bin/env python3
"""
Code review CLI.

Usage:
    ./cli.py --files "app/Models/User.php"
    ./cli.py --files "app/Models/*.php" --task "Added user feature"
    ./cli.py --files "app/Services/UserService.php" --session my-review-123
    ./cli.py --files "app/Models/User.php" --json --output ./review.json
"""

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.models import CodeReviewOptions
from src.services import CodeReviewService, CodeReviewSessionManager

CODE_REVIEWER_DIR = Path(__file__).parent.resolve()
PROMPT_PATH = CODE_REVIEWER_DIR / "prompt.md"
CONFIG_PATH = CODE_REVIEWER_DIR / "config.json"


def get_sessions_path() -> Path:
    """
    Get the sessions path from config or use default.

    Config output_dir can be:
    - Relative path: Resolved from project root
    - Absolute path: Used as-is
    - Not specified: Defaults to tool's sessions/ directory
    """
    if not CONFIG_PATH.exists():
        return CODE_REVIEWER_DIR / "sessions"

    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError):
        return CODE_REVIEWER_DIR / "sessions"

    output_dir = config.get("output_dir")
    if not output_dir:
        return CODE_REVIEWER_DIR / "sessions"

    output_path = Path(output_dir)
    if output_path.is_absolute():
        return output_path / "sessions"

    # Relative paths resolved from project root
    # CODE_REVIEWER_DIR -> devtools -> project_root
    project_root = CODE_REVIEWER_DIR.parent.parent
    return project_root / output_path / "sessions"


SESSIONS_PATH = get_sessions_path()


def get_git_info(cwd: Path | None = None) -> tuple[str | None, str | None]:
    """
    Get current git branch and commit hash.

    Args:
        cwd: Working directory for git commands

    Returns:
        Tuple of (branch, commit_hash) or (None, None) on error
    """
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd,
        ).stdout.strip()

        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd,
        ).stdout.strip()

        return branch, commit
    except Exception:
        return None, None


# Allowed tools (including Serena MCP)
ALLOWED_TOOLS = [
    "Read",
    "Bash",
    "Glob",
    "Grep",
    "mcp__serena__find_symbol",
    "mcp__serena__get_symbols_overview",
    "mcp__serena__find_referencing_symbols",
    "mcp__serena__search_for_pattern",
    "mcp__serena__list_dir",
    "mcp__serena__find_file",
]


def get_serena_config(project_dir: Path) -> dict[str, Any]:
    """
    Build Serena MCP server configuration.

    Args:
        project_dir: Project root directory

    Returns:
        MCP server config dict for Serena
    """
    # Find uvx binary
    uvx_path = shutil.which("uvx")
    if not uvx_path:
        # Try common locations
        home = Path.home()
        for candidate in [
            home / ".local/bin/uvx",
            home / ".cargo/bin/uvx",
            Path("/usr/local/bin/uvx"),
        ]:
            if candidate.exists():
                uvx_path = str(candidate)
                break

    if not uvx_path:
        uvx_path = "uvx"  # Hope it's in PATH

    return {
        "command": uvx_path,
        "args": [
            "--from",
            "git+https://github.com/oraios/serena",
            "serena",
            "start-mcp-server",
            "--project",
            str(project_dir),
            "--context",
            "ide-assistant",
            "--enable-web-dashboard",
            "False",
        ],
    }


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run code review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--files", "-f",
        required=True,
        help="Files to review (comma-separated or description)",
    )
    parser.add_argument(
        "--task", "-t",
        default="",
        help="Description of what was being done (context)",
    )
    parser.add_argument(
        "--session", "-s",
        help="Session ID (auto-generated if not provided)",
    )
    parser.add_argument(
        "--output", "-o",
        help="Path to save the review result as JSON",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON to stdout",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only output on failure",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose logging to stderr",
    )

    return parser.parse_args()


async def run_review(args: argparse.Namespace) -> int:
    """Run the review and return exit code."""
    # Get project directory and git info
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", str(Path.cwd())))
    git_branch, git_commit = get_git_info(project_dir)

    # Create session
    session_manager = CodeReviewSessionManager(SESSIONS_PATH)
    session, logger = session_manager.create_session(
        session_id=args.session,
        verbose=args.verbose,
        git_branch=git_branch,
        git_commit=git_commit,
    )

    logger.info(f"Session: {session.session_id}")

    # Configure options with Serena MCP
    options = CodeReviewOptions(
        prompt_template_path=PROMPT_PATH,
        cwd=project_dir,
        allowed_tools=ALLOWED_TOOLS,
        mcp_servers={"serena": get_serena_config(project_dir)},
    )

    # Run review
    service = CodeReviewService(options, logger)

    try:
        result = await service.review(
            files=args.files,
            original_task=args.task,
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.close()
        return 2
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.close()
        return 2

    # Track input and result in session
    session.review_input = args.files
    session.completed_at = result.completed_at.isoformat()
    session.decision = "passed" if result.passed else "blocked"
    session.duration_ms = result.duration_ms
    session.input_tokens = result.input_tokens
    session.output_tokens = result.output_tokens
    session.total_cost_usd = result.total_cost_usd
    session_manager.save_session(session)

    # Output result
    result_data = result.to_dict()

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(result_data, f, indent=2)

    if args.json:
        print(json.dumps(result_data, indent=2))
    elif not args.quiet or result.has_issues:
        print(result.review_text)

    logger.close()

    # Exit code: 0 = passed, 1 = blocked
    return 1 if result.has_issues else 0


def main() -> int:
    """Main entry point."""
    args = parse_args()
    try:
        return asyncio.run(run_review(args))
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
