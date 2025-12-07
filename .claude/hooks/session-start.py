#!/usr/bin/env python3
"""
Claude Code hook that runs at session start.

This hook runs when a new Claude Code session begins and can be used to:
- Display project-specific reminders
- Check environment setup
- Validate required tools are available
"""

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hook_logger import HookLogger


def check_tool_available(tool_path: str, project_dir: str) -> bool:
    """Check if a tool exists and is executable."""
    full_path = os.path.join(project_dir, tool_path)
    return os.path.exists(full_path) and os.access(full_path, os.X_OK)


def main():
    """Main entry point for the session-start hook."""
    try:
        hook_input = json.load(sys.stdin)
        session_id = hook_input.get("session_id")
        project_dir = hook_input.get("cwd", os.getcwd())

        logger = HookLogger("session-start", session_id=session_id)
        logger.info("Session started")

        # Check available tools
        tools = {
            "pint": "vendor/bin/pint",
            "phpstan": "vendor/bin/phpstan",
            "rector": "vendor/bin/rector",
        }

        available = []
        for name, path in tools.items():
            if check_tool_available(path, project_dir):
                available.append(name)

        if available:
            logger.info(f"Available tools: {', '.join(available)}")

        # Check for node_modules (eslint/prettier)
        node_modules = os.path.join(project_dir, "node_modules")
        if os.path.exists(node_modules):
            logger.info("Node modules available for JS/TS linting")

        logger.success("Session initialized successfully")

    except Exception as e:
        # Create logger without session_id for error case
        logger = HookLogger("session-start")
        logger.error(f"Session start hook failed: {str(e)}")

    # Always exit 0 - session start should never block
    sys.exit(0)


if __name__ == "__main__":
    main()
