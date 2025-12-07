#!/usr/bin/env python3
"""
Reusable logging utility for Claude Code hooks.

Provides a centralized logging mechanism for all hook scripts with:
- Timestamped entries
- Structured formatting
- Shared log file
- Easy-to-use API
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class HookLogger:
    """
    A reusable logger for Claude Code hooks.

    Usage:
        logger = HookLogger("format-php", session_id="abc123")
        logger.info("Starting PHP formatting")
        logger.success("Formatted MyFile.php", details="Found 5 issues")
        logger.error("Failed to format", details="Syntax error")
    """

    def __init__(self, hook_name: str, session_id: Optional[str] = None, log_file: Optional[str] = None):
        """
        Initialize the logger.

        Args:
            hook_name: Name of the hook (e.g., "format-php", "run-tests")
            session_id: The Claude session ID (truncated to 8 chars in logs)
            log_file: Path to log file (defaults to .claude/sessions/{session_id}/hooks.log)
        """
        self.hook_name = hook_name
        self.session_id_short = session_id[:8] if session_id else "--------"
        self.session_id_full = session_id

        if log_file is None:
            script_dir = Path(__file__).parent
            if session_id:
                # Session-specific log file
                session_dir = script_dir.parent / "sessions" / session_id
                session_dir.mkdir(parents=True, exist_ok=True)
                self.log_file = session_dir / "hooks.log"
            else:
                # Fallback to hooks directory for errors without session
                self.log_file = script_dir / "hooks.log"
        else:
            self.log_file = Path(log_file)

        # Ensure log file directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def _write_log(self, level: str, message: str, details: Optional[str] = None):
        """Write a log entry to the log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Format the log entry (no session_id needed since it's in the path now)
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
