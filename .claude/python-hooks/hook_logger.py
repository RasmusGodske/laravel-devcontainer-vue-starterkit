#!/usr/bin/env python3
"""
Reusable logging utility for Claude Code hooks.

Provides a centralized logging mechanism for all hook scripts with:
- Timestamped entries
- Structured formatting
- Shared log file
- Easy-to-use API
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class HookLogger:
    """
    A reusable logger for Claude Code hooks.

    Usage:
        logger = HookLogger("format-php")
        logger.info("Starting PHP formatting")
        logger.success("Formatted MyFile.php", details="Found 5 issues")
        logger.error("Failed to format", details="Syntax error")
    """

    def __init__(self, hook_name: str, log_file: Optional[str] = None):
        """
        Initialize the logger.

        Args:
            hook_name: Name of the hook (e.g., "format-php", "run-tests")
            log_file: Path to log file (defaults to .claude/python-hooks/hooks.log)
        """
        self.hook_name = hook_name

        if log_file is None:
            script_dir = Path(__file__).parent
            self.log_file = script_dir / "hooks.log"
        else:
            self.log_file = Path(log_file)

        # Ensure log file directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def _write_log(self, level: str, message: str, details: Optional[str] = None):
        """Write a log entry to the log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Format the log entry
        log_entry = f"[{timestamp}] [{level}] [{self.hook_name}] {message}"

        if details:
            # Indent details for readability
            details_lines = details.strip().split('\n')
            formatted_details = '\n'.join(f"    {line}" for line in details_lines)
            log_entry += f"\n{formatted_details}"

        log_entry += "\n"

        # Append to log file
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            # If logging fails, write to stderr but don't crash
            print(f"Failed to write to log: {e}", file=sys.stderr)

    def info(self, message: str, details: Optional[str] = None):
        """Log an informational message."""
        self._write_log("INFO", message, details)

    def success(self, message: str, details: Optional[str] = None):
        """Log a success message."""
        self._write_log("SUCCESS", message, details)

    def warning(self, message: str, details: Optional[str] = None):
        """Log a warning message."""
        self._write_log("WARNING", message, details)

    def error(self, message: str, details: Optional[str] = None):
        """Log an error message."""
        self._write_log("ERROR", message, details)

    def separator(self):
        """Write a separator line for visual clarity."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write("-" * 80 + "\n")
        except Exception:
            pass


# Convenience function for one-off logging
def quick_log(hook_name: str, message: str, level: str = "INFO", details: Optional[str] = None):
    """
    Quick logging without creating a logger instance.

    Args:
        hook_name: Name of the hook
        message: Log message
        level: Log level (INFO, SUCCESS, WARNING, ERROR)
        details: Optional additional details
    """
    logger = HookLogger(hook_name)

    if level.upper() == "SUCCESS":
        logger.success(message, details)
    elif level.upper() == "WARNING":
        logger.warning(message, details)
    elif level.upper() == "ERROR":
        logger.error(message, details)
    else:
        logger.info(message, details)


if __name__ == "__main__":
    # Test the logger
    logger = HookLogger("test-hook")
    logger.info("This is an info message")
    logger.success("This is a success message", details="With some details")
    logger.warning("This is a warning")
    logger.error("This is an error", details="Stack trace here\nLine 2\nLine 3")
    logger.separator()

    print(f"Test logs written to: {logger.log_file}")
