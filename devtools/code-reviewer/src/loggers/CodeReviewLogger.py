"""
Session-scoped logger for code reviews.
"""

import logging
from pathlib import Path


class CodeReviewLogger:
    """
    Logger scoped to a code review session.

    Writes logs to the session directory: sessions/{session-id}/log.txt

    Example:
        logger = CodeReviewLogger(
            session_id="review-20251210-a1b2c3",
            log_path=Path("sessions/review-20251210-a1b2c3/log.txt"),
        )
        logger.info("Starting review")
        logger.info("Reviewing file: app/Models/User.php")
        logger.close()

    Or with context manager:
        with CodeReviewLogger(session_id, log_path) as logger:
            logger.info("Starting review")
    """

    def __init__(
        self,
        session_id: str,
        log_path: Path,
        verbose: bool = False,
    ) -> None:
        """
        Initialize the logger.

        Args:
            session_id: Session identifier (used for unique logger name)
            log_path: Path to the log file
            verbose: If True, also output to stderr
        """
        self._session_id = session_id
        self._log_path = log_path
        self._verbose = verbose
        self._logger: logging.Logger | None = None
        self._file_handler: logging.FileHandler | None = None
        self._is_initialized = False

    @property
    def logger_name(self) -> str:
        """Unique name for this logger instance."""
        return f"code-reviewer.session.{self._session_id}"

    def _ensure_initialized(self) -> None:
        """Initialize the logger on first use (lazy initialization)."""
        if self._is_initialized:
            return

        # Ensure log directory exists
        self._log_path.parent.mkdir(parents=True, exist_ok=True)

        # Create logger with unique name
        self._logger = logging.getLogger(self.logger_name)
        self._logger.setLevel(logging.DEBUG)
        self._logger.handlers.clear()
        self._logger.propagate = False

        # File handler
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self._file_handler = logging.FileHandler(
            self._log_path,
            mode="a",
            encoding="utf-8",
        )
        self._file_handler.setLevel(logging.DEBUG)
        self._file_handler.setFormatter(formatter)
        self._logger.addHandler(self._file_handler)

        # Stderr handler (optional)
        if self._verbose:
            stderr_handler = logging.StreamHandler()
            stderr_handler.setLevel(logging.DEBUG)
            stderr_handler.setFormatter(
                logging.Formatter("%(levelname)s: %(message)s")
            )
            self._logger.addHandler(stderr_handler)

        self._is_initialized = True

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self._ensure_initialized()
        if self._logger:
            self._logger.debug(message)

    def info(self, message: str) -> None:
        """Log an info message."""
        self._ensure_initialized()
        if self._logger:
            self._logger.info(message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self._ensure_initialized()
        if self._logger:
            self._logger.warning(message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self._ensure_initialized()
        if self._logger:
            self._logger.error(message)

    def exception(self, message: str) -> None:
        """Log an exception with traceback."""
        self._ensure_initialized()
        if self._logger:
            self._logger.exception(message)

    def close(self) -> None:
        """Close the logger and release resources."""
        if self._logger:
            for handler in self._logger.handlers[:]:
                handler.close()
                self._logger.removeHandler(handler)
        self._file_handler = None
        self._is_initialized = False

    def __enter__(self) -> "CodeReviewLogger":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: object) -> None:
        """Context manager exit - close the logger."""
        self.close()
