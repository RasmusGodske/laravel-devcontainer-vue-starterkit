#!/usr/bin/env python3
"""
Claude Code hook for reminding to re-read rules after compaction.

This hook runs before compact operations and injects a message to remind
Claude to re-read all relevant rules from .claude/rules/ to ensure proper
adherence to project conventions after context is compacted.

Usage:
    Called automatically by Claude Code PreCompact hook.
"""

import json
import sys
from pathlib import Path

# Add the script directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the reusable logger
from hook_logger import HookLogger


def main():
    """Main entry point for the remind-rules hook."""
    logger = HookLogger("remind-rules")

    try:
        # Read hook input from stdin
        hook_input = json.load(sys.stdin)

        # Log that we're sending the reminder
        logger.info("Compaction detected - sending rules reminder to Claude")

        # Print the message to stdout - this will be shown to Claude when exit code is 0
        message = (
            "🔄 The conversation has been compacted. "
            "Please re-read ALL relevant rules from `.claude/rules/` to ensure you continue "
            "following project conventions correctly. This includes backend rules, frontend rules, "
            "and data class patterns."
        )

        print(message)

        logger.success("Rules reminder sent to Claude via stdout")

        # Exit with code 0 so the stdout is shown to Claude
        sys.exit(0)

    except Exception as e:
        logger.error(f"Failed to send rules reminder: {str(e)}")
        # Exit with 0 anyway to not break the session
        sys.exit(0)


if __name__ == "__main__":
    main()
