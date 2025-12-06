#!/usr/bin/env python3
"""
Claude Code hook for automatically validating and formatting PHP files.

This hook runs after Write or Edit operations on PHP files and:
1. Detects if the file is a PHP file
2. Validates PHP syntax with php -l (blocks operation if invalid)
3. Runs Rector to add missing imports (if available)
4. Runs Laravel Pint to format it
5. Logs the results to hooks.log

Usage:
    Called automatically by Claude Code PostToolUse hook.
    Receives JSON input via stdin with tool_input containing file_path.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Add the script directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the reusable logger
from hook_logger import HookLogger


def validate_php_syntax(file_path, project_dir, logger, file_name):
    """
    Validate PHP syntax using php -l.

    Exits with error code 1 if syntax errors are found, blocking the operation.
    """
    lint_command = [
        "php",
        "-l",
        file_path
    ]

    logger.info(f"Validating PHP syntax for {file_name}")

    lint_result = subprocess.run(
        lint_command,
        cwd=project_dir,
        capture_output=True,
        text=True,
        timeout=10
    )

    if lint_result.returncode != 0:
        # Syntax error found - block the operation
        error_output = lint_result.stdout + lint_result.stderr
        logger.error(
            f"PHP syntax error in {file_name}",
            details=error_output.strip()
        )
        # Exit with error code 1 to block the Write/Edit operation
        sys.exit(1)

    logger.success(f"PHP syntax valid for {file_name}")
    return True


def main():
    """Main entry point for the format-php hook."""
    logger = HookLogger("format-php")

    try:
        # Read hook input from stdin
        hook_input = json.load(sys.stdin)

        # Extract file path from tool input
        tool_input = hook_input.get("tool_input", {})
        file_path = tool_input.get("file_path")

        if not file_path:
            # Not a file operation, skip silently
            return

        # Check if it's a PHP file
        if not file_path.endswith(".php"):
            # Not a PHP file, skip silently
            return

        # Get just the filename for logging
        file_name = Path(file_path).name

        logger.info(f"Processing {file_name}")

        # Get project directory
        project_dir = hook_input.get("cwd", os.getcwd())

        # Convert to relative path if it's absolute
        if os.path.isabs(file_path):
            relative_file_path = os.path.relpath(file_path, project_dir)
        else:
            relative_file_path = file_path

        # Step 1: Validate PHP syntax (blocks operation if invalid)
        validate_php_syntax(relative_file_path, project_dir, logger, file_name)

        # Step 2: Run Rector to add missing imports (if available)
        rector_path = os.path.join(project_dir, "vendor/bin/rector")
        imports_added = False

        if os.path.exists(rector_path):
            rector_command = [
                "php",
                "vendor/bin/rector",
                "process",
                relative_file_path,
                "--no-progress-bar"
            ]

            rector_result = subprocess.run(
                rector_command,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=30
            )

            rector_output = rector_result.stdout + rector_result.stderr
            imports_added = "changed" in rector_output.lower() or "file" in rector_output.lower()

            if imports_added:
                logger.info(f"Rector added imports to {file_name}")

        # Step 3: Run Pint to format the file
        pint_command = [
            "./vendor/bin/pint",
            relative_file_path
        ]

        pint_result = subprocess.run(
            pint_command,
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30
        )

        # Parse Pint output to extract issue count
        pint_output = pint_result.stdout + pint_result.stderr
        issues_fixed = None

        if "style issues fixed" in pint_output or "style issue fixed" in pint_output:
            # Try to extract the number
            for line in pint_output.split('\n'):
                if "style issue" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "style" in part and i > 0:
                            try:
                                issues_fixed = int(parts[i - 1])
                                break
                            except ValueError:
                                pass

        # Log the final result
        if pint_result.returncode == 0:
            if issues_fixed is not None and issues_fixed > 0:
                logger.success(
                    f"Formatted {file_name}",
                    details=f"Pint fixed {issues_fixed} style issue{'s' if issues_fixed != 1 else ''}"
                )
            elif imports_added:
                logger.success(f"Added imports to {file_name}")
            else:
                logger.info(f"No changes needed for {file_name}")
        else:
            # Pint failed
            logger.error(
                f"Failed to format {file_name}",
                details=pint_output.strip() if pint_output.strip() else "Unknown error"
            )

    except json.JSONDecodeError:
        logger.error("Failed to parse hook input JSON")
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout while processing {file_name}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
