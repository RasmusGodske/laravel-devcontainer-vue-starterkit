"""
Base logger class providing common logging functionality.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Optional


class BaseLogger(ABC):
    """
    Abstract base class for all loggers in the subagent-reviewer system.

    Provides common logging functionality while allowing subclasses to define
    their specific log file paths based on their context (global, session, review).
    """

    def __init__(self, verbose: bool = False, also_stderr: bool = False):
        """
        Initialize the base logger.

        Args:
            verbose: If True, set DEBUG level; otherwise INFO
            also_stderr: If True, also log to stderr
        """
        self._verbose = verbose
        self._also_stderr = also_stderr
        self._logger: Optional[logging.Logger] = None
        self._file_handler: Optional[logging.FileHandler] = None
        self._initialized = False

    @property
    @abstractmethod
    def log_path(self) -> Path:
        """Return the path to the log file. Must be implemented by subclasses."""
        pass

    @property
    @abstractmethod
    def logger_name(self) -> str:
        """Return a unique name for this logger instance."""
        pass

    def _get_formatter(self) -> logging.Formatter:
        """Get the log formatter."""
        return logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def _ensure_initialized(self) -> None:
        """Ensure the logger is initialized before use."""
        if self._initialized:
            return

        # Ensure log directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # Create logger with unique name
        self._logger = logging.getLogger(self.logger_name)
        self._logger.setLevel(logging.DEBUG)

        # Clear any existing handlers
        self._logger.handlers.clear()

        # Prevent propagation to root logger
        self._logger.propagate = False

        # File handler
        self._file_handler = logging.FileHandler(
            self.log_path,
            mode='a',
            encoding='utf-8'
        )
        self._file_handler.setLevel(logging.DEBUG)
        self._file_handler.setFormatter(self._get_formatter())
        self._logger.addHandler(self._file_handler)

        # Stderr handler (optional)
        if self._also_stderr:
            stderr_handler = logging.StreamHandler()
            stderr_handler.setLevel(logging.DEBUG if self._verbose else logging.INFO)
            stderr_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
            self._logger.addHandler(stderr_handler)

        self._initialized = True

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self._ensure_initialized()
        self._logger.debug(message)

    def info(self, message: str) -> None:
        """Log an info message."""
        self._ensure_initialized()
        self._logger.info(message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self._ensure_initialized()
        self._logger.warning(message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self._ensure_initialized()
        self._logger.error(message)

    def exception(self, message: str) -> None:
        """Log an exception with traceback."""
        self._ensure_initialized()
        self._logger.exception(message)

    def close(self) -> None:
        """Close the logger and release resources."""
        if self._logger:
            for handler in self._logger.handlers[:]:
                handler.close()
                self._logger.removeHandler(handler)
        self._file_handler = None
        self._initialized = False

    def __enter__(self) -> "BaseLogger":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - close the logger."""
        self.close()
