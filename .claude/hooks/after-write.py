#!/usr/bin/env python3
"""
Claude Code hook that runs after Write/Edit operations.

1. Records the file to the session tracker (for end-of-turn checks)
2. Runs syntax validation:
   - PHP: php -l (syntax check) - blocks on errors
   - JS/TS/Vue: just track, no immediate check

Uses JSON output to provide feedback to Claude:
- Syntax errors: block with reason (Claude must fix)
- Other issues: gentle feedback (Claude can decide)

Formatting (Pint, ESLint) is deferred to end-of-turn.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import HookLogger
from session_tracker import SessionTracker, get_file_type


def output_json(data: dict):
    """Output JSON response and exit with code 0."""
    print(json.dumps(data))
    sys.exit(0)


def output_block(reason: str):
    """Block the operation with a reason shown to Claude."""
    output_json({
        "decision": "block",
        "reason": reason
    })


def run_command(cmd: list, cwd: str, timeout: int = 30) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def check_php_syntax(file_path: str, project_dir: str, logger: HookLogger) -> tuple[bool, str]:
    """
    Check PHP syntax. Returns (success, error_message).
    """
    rel_path = os.path.relpath(file_path, project_dir) if os.path.isabs(file_path) else file_path
    file_name = Path(file_path).name

    code, stdout, stderr = run_command(["php", "-l", rel_path], project_dir, timeout=10)
    if code != 0:
        error_msg = (stdout + stderr).strip()
        logger.error(f"PHP syntax error in {file_name}", details=error_msg)
        return False, error_msg

    logger.success(f"Syntax OK: {file_name}")
    return True, ""


def main():
    """Main entry point for the after-write hook."""
    try:
        hook_input = json.load(sys.stdin)

        tool_input = hook_input.get("tool_input", {})
        file_path = tool_input.get("file_path")
        session_id = hook_input.get("session_id")
        project_dir = hook_input.get("cwd", os.getcwd())

        logger = HookLogger("after-write", session_id=session_id)

        if not file_path:
            sys.exit(0)

        # Check if file exists (might have been a failed write)
        full_path = file_path if os.path.isabs(file_path) else os.path.join(project_dir, file_path)
        if not os.path.exists(full_path):
            sys.exit(0)

        # Track this file in the session
        file_type = get_file_type(file_path)
        if session_id and file_type != "other":
            tracker = SessionTracker(session_id)
            tracker.add_file(full_path, file_type)
            logger.info(f"Tracked {Path(file_path).name} in session {tracker.session.short_id}...")

        # Run syntax check for PHP - block on errors
        if file_type == "php":
            success, error_msg = check_php_syntax(file_path, project_dir, logger)
            if not success:
                file_name = Path(file_path).name
                output_block(f"PHP syntax error in {file_name}:\n{error_msg}\n\nPlease fix the syntax error.")

    except json.JSONDecodeError:
        HookLogger("after-write").error("Failed to parse hook input JSON")
    except Exception as e:
        HookLogger("after-write").error(f"Unexpected error: {str(e)}")

    sys.exit(0)


if __name__ == "__main__":
    main()
