#!/usr/bin/env python3
"""
Claude Code hook that runs when Claude finishes responding.

Logs the stop event to provide context in the session's hooks.log file.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import HookLogger


def main():
    """Main entry point for the stop hook."""
    try:
        hook_input = json.load(sys.stdin)

        session_id = hook_input.get("session_id")
        stop_hook_active = hook_input.get("stop_hook_active", False)

        logger = HookLogger("stop", session_id=session_id)

        if stop_hook_active:
            logger.info("Claude finished responding (stop_hook_active=true)")
        else:
            logger.info("Claude finished responding")

    except json.JSONDecodeError:
        HookLogger("stop").error("Failed to parse hook input JSON")
    except Exception as e:
        HookLogger("stop").error(f"Unexpected error: {str(e)}")

    # Always exit 0 - never block
    sys.exit(0)


if __name__ == "__main__":
    main()
