#!/usr/bin/env python3
"""
Claude Code hook that runs at end of turn (Stop event).

Reads the session tracker to find files modified THIS session, then runs:
- Pint for PHP formatting
- PHPStan for static analysis on PHP files
- ESLint --fix for JS/TS/Vue files

Uses JSON output to provide feedback to Claude:
- "decision": "block" with reason - Claude sees feedback and can fix issues
- Clears session tracker after successful checks
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hook_logger import HookLogger
from session_tracker import SessionTracker


def output_json(data: dict):
    """Output JSON response and exit with code 0."""
    print(json.dumps(data))
    sys.exit(0)


def output_block(reason: str):
    """Block with a reason shown to Claude."""
    output_json({
        "decision": "block",
        "reason": reason
    })


def run_command(cmd: list, cwd: str, timeout: int = 120) -> tuple[int, str, str]:
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


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"


def run_pint(files: list[str], project_dir: str, logger: HookLogger) -> bool:
    """
    Run Pint to format PHP files.
    Returns True if successful.
    """
    pint_path = os.path.join(project_dir, "vendor/bin/pint")
    if not os.path.exists(pint_path) or not files:
        return True

    # Convert to relative paths
    rel_files = []
    for f in files:
        if os.path.exists(f):
            rel_files.append(os.path.relpath(f, project_dir))

    if not rel_files:
        return True

    logger.info(f"[START] Pint on {len(rel_files)} PHP file(s)")

    start_time = time.time()
    cmd = ["./vendor/bin/pint"] + rel_files
    code, stdout, stderr = run_command(cmd, project_dir, timeout=60)
    duration = time.time() - start_time

    output = (stdout + stderr).strip()

    if code != 0:
        logger.warning(f"[DONE] Pint had issues ({format_duration(duration)})", details=output)
    else:
        logger.success(f"[DONE] Pint formatting complete ({format_duration(duration)})")

    return True  # Pint formatting issues shouldn't block


def run_phpstan(project_dir: str, logger: HookLogger) -> tuple[bool, str]:
    """
    Run PHPStan on the entire project.
    This catches cascading issues from modified files affecting other files.
    Returns (success, error_output).
    """
    phpstan_path = os.path.join(project_dir, "vendor/bin/phpstan")
    if not os.path.exists(phpstan_path):
        return True, ""

    logger.info("[START] PHPStan on entire project")

    start_time = time.time()
    cmd = ["./vendor/bin/phpstan", "analyse", "--no-progress", "--error-format=table"]
    code, stdout, stderr = run_command(cmd, project_dir, timeout=180)
    duration = time.time() - start_time

    output = (stdout + stderr).strip()

    if code != 0:
        if "[ERROR]" in output or " error" in output.lower():
            logger.error(f"[DONE] PHPStan found issues ({format_duration(duration)})", details=output)
            return False, output

    logger.success(f"[DONE] PHPStan passed ({format_duration(duration)})")
    return True, ""


def run_eslint(files: list[str], project_dir: str, logger: HookLogger) -> tuple[bool, str]:
    """
    Run ESLint --fix on the given files.
    Returns (success, error_output).
    """
    eslint_bin = os.path.join(project_dir, "node_modules/.bin/eslint")
    if not os.path.exists(eslint_bin) or not files:
        return True, ""

    # Convert to relative paths
    rel_files = []
    for f in files:
        if os.path.exists(f):
            rel_files.append(os.path.relpath(f, project_dir))

    if not rel_files:
        return True, ""

    logger.info(f"[START] ESLint --fix on {len(rel_files)} JS/TS/Vue file(s)")

    start_time = time.time()
    cmd = ["node_modules/.bin/eslint", "--fix"] + rel_files
    code, stdout, stderr = run_command(cmd, project_dir, timeout=60)
    duration = time.time() - start_time

    output = (stdout + stderr).strip()

    # After --fix, re-check if there are remaining errors
    if code != 0 and output:
        logger.error(f"[DONE] ESLint found unfixable issues ({format_duration(duration)})", details=output)
        return False, output

    logger.success(f"[DONE] ESLint passed ({format_duration(duration)})")
    return True, ""


def main():
    """Main entry point for the end-of-turn-check hook."""
    try:
        hook_input = json.load(sys.stdin)

        session_id = hook_input.get("session_id")
        stop_hook_active = hook_input.get("stop_hook_active", False)

        logger = HookLogger("end-of-turn", session_id=session_id)
        logger.separator()

        # Prevent infinite loops - if we're already in a stop hook, skip
        if stop_hook_active:
            logger.info("Stop hook already active, skipping to prevent loop")
            sys.exit(0)

        if not session_id:
            logger.warning("No session_id provided")
            sys.exit(0)

        # Get project directory - Stop hook doesn't have cwd, so we derive it
        # from the hooks directory location
        hooks_dir = Path(__file__).parent
        project_dir = str(hooks_dir.parent.parent)  # .claude/hooks -> .claude -> project

        logger.info(f"Running end-of-turn checks for session {session_id[:8]}...")

        # Load files from session tracker
        tracker = SessionTracker(session_id)
        files_by_type = tracker.get_files_by_type()

        php_files = files_by_type.get("php", [])
        js_files = files_by_type.get("js", [])

        if not php_files and not js_files:
            logger.info("No PHP/JS files modified this session")
            sys.exit(0)

        logger.info(f"Found {len(php_files)} PHP and {len(js_files)} JS/TS/Vue files")

        errors = []

        # Run Pint first to format PHP files
        if php_files:
            run_pint(php_files, project_dir, logger)

        # Run PHPStan on entire project (catches cascading issues)
        if php_files:
            success, output = run_phpstan(project_dir, logger)
            if not success:
                errors.append(f"PHPStan errors:\n{output}")

        # Run ESLint on JS/TS/Vue files
        if js_files:
            success, output = run_eslint(js_files, project_dir, logger)
            if not success:
                errors.append(f"ESLint errors:\n{output}")

        if errors:
            error_report = "\n\n".join(errors)
            logger.error("End-of-turn checks failed")
            output_block(f"End-of-turn checks found issues:\n\n{error_report}\n\nPlease fix these issues before continuing.")

        # All checks passed - clear the session tracker
        tracker.clear()
        logger.success("All end-of-turn checks passed")

    except json.JSONDecodeError:
        HookLogger("end-of-turn").error("Failed to parse hook input JSON")
    except Exception as e:
        HookLogger("end-of-turn").error(f"Unexpected error: {str(e)}")

    sys.exit(0)


if __name__ == "__main__":
    main()
