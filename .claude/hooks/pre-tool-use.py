#!/usr/bin/env python3
"""
Claude Code hook that runs before a tool is used.

Logs the tool name and key input info to provide context in hooks.log.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hook_logger import HookLogger


def get_tool_summary(tool_name: str, tool_input: dict) -> str:
    """Get a concise summary of the tool usage."""
    if tool_name in ["Write", "Edit"]:
        file_path = tool_input.get("file_path", "unknown")
        return f"{tool_name}: {Path(file_path).name}"

    elif tool_name == "Read":
        file_path = tool_input.get("file_path", "unknown")
        return f"{tool_name}: {Path(file_path).name}"

    elif tool_name == "Bash":
        command = tool_input.get("command", "")
        # Truncate long commands
        if len(command) > 80:
            command = command[:80] + "..."
        return f"{tool_name}: {command}"

    elif tool_name == "Glob":
        pattern = tool_input.get("pattern", "")
        return f"{tool_name}: {pattern}"

    elif tool_name == "Grep":
        pattern = tool_input.get("pattern", "")
        return f"{tool_name}: {pattern}"

    elif tool_name == "Task":
        description = tool_input.get("description", "")
        return f"{tool_name}: {description}"

    else:
        # For other tools, just show the name
        return tool_name


def main():
    """Main entry point for the pre-tool-use hook."""
    try:
        hook_input = json.load(sys.stdin)

        session_id = hook_input.get("session_id")
        tool_name = hook_input.get("tool_name", "unknown")
        tool_input = hook_input.get("tool_input", {})

        logger = HookLogger("tool", session_id=session_id)

        summary = get_tool_summary(tool_name, tool_input)
        logger.info(summary)

    except json.JSONDecodeError:
        HookLogger("tool").error("Failed to parse hook input JSON")
    except Exception as e:
        HookLogger("tool").error(f"Unexpected error: {str(e)}")

    # Always exit 0 - never block tool use from this hook
    sys.exit(0)


if __name__ == "__main__":
    main()
