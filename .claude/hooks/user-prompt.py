#!/usr/bin/env python3
"""
Claude Code hook that runs when user submits a prompt.

Logs the prompt to provide context in the hooks.log file.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import HookLogger


def main():
    """Main entry point for the user-prompt hook."""
    try:
        hook_input = json.load(sys.stdin)

        session_id = hook_input.get("session_id")
        prompt = hook_input.get("prompt", "")

        logger = HookLogger("user-prompt", session_id=session_id)
        logger.separator()

        # Truncate long prompts for readability
        prompt_display = prompt

        logger.info(f"User: {prompt_display}")

    except json.JSONDecodeError:
        HookLogger("user-prompt").error("Failed to parse hook input JSON")
    except Exception as e:
        HookLogger("user-prompt").error(f"Unexpected error: {str(e)}")

    # Always exit 0 - never block user prompts
    sys.exit(0)


if __name__ == "__main__":
    main()
