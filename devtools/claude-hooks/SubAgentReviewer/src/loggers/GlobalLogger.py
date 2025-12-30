"""
Global logger that writes to the main hook.log file.
"""

from pathlib import Path

from .BaseLogger import BaseLogger
from ..Paths import Paths


class GlobalLogger(BaseLogger):
    """
    Logger for global hook events.

    Writes to: devtools/claude-hooks/SubAgentReviewer2/hook.log

    Use this logger for:
    - Hook startup/shutdown events
    - Errors that occur before session context is established
    - Summary statistics across all sessions

    Example:
        logger = GlobalLogger()
        logger.info("Hook started")
        logger.info("Processing session: abc123")
    """

    def __init__(
        self,
        paths: Paths | None = None,
        verbose: bool = False,
        also_stderr: bool = False,
    ):
        """
        Initialize the global logger.

        Args:
            paths: Paths instance for path resolution. Creates default if None.
            verbose: If True, set DEBUG level; otherwise INFO
            also_stderr: If True, also log to stderr
        """
        super().__init__(verbose=verbose, also_stderr=also_stderr)
        self._paths = paths or Paths()

    @property
    def log_path(self) -> Path:
        """Return the path to the global log file."""
        return self._paths.global_log

    @property
    def logger_name(self) -> str:
        """Return the logger name."""
        return "subagent-reviewer.global"

    # =========================================================================
    # Convenience Methods for Common Log Patterns
    # =========================================================================

    def log_hook_start(self, session_id: str, event_name: str) -> None:
        """Log hook invocation start."""
        self.info(f"{'='*60}")
        self.info(f"Hook triggered: {event_name}")
        self.info(f"Session: {session_id}")

    def log_hook_end(self, session_id: str, decision: str, duration_ms: int) -> None:
        """Log hook completion."""
        self.info(f"Decision: {decision}")
        self.info(f"Duration: {duration_ms}ms")
        self.info(f"Session {session_id} complete")
        self.info(f"{'='*60}")
