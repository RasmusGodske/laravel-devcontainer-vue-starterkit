#!/usr/bin/env python3
"""
Session tracking for Claude Code hooks.

Provides SessionTracker for managing session state and tracking modified files.
Data classes are in the data/ subdirectory.

Usage:
    from session_tracker import SessionTracker, Session, TrackedFile, get_file_type

    tracker = SessionTracker(session_id)
    tracker.add_file("/path/to/file.php", "php")

    session = tracker.session
    php_files = session.php_files

    tracker.save()
    tracker.clear()
"""

import json
import shutil
from pathlib import Path
from typing import Optional

from data import Session, TrackedFile

# Re-export for backwards compatibility
__all__ = ["SessionTracker", "Session", "TrackedFile", "get_file_type"]


class SessionTracker:
    """
    Manages session persistence and provides access to Session data.

    Handles loading/saving session state to disk.
    """

    def __init__(self, session_id: str, base_dir: Optional[str] = None):
        """
        Initialize the session tracker.

        Args:
            session_id: The Claude session ID
            base_dir: Base directory for sessions (defaults to .claude/sessions)
        """
        if base_dir is None:
            hooks_dir = Path(__file__).parent
            sessions_base = hooks_dir.parent / "sessions"
        else:
            sessions_base = Path(base_dir)

        self.session_dir = sessions_base / session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.session_dir / "session.json"

        # Load or create session
        self._session = self._load()

    def _load(self) -> Session:
        """Load session from file or create new one."""
        if self.session_file.exists():
            try:
                with open(self.session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return Session.from_dict(data)
            except (json.JSONDecodeError, IOError):
                pass

        # Return new session with ID from directory name
        return Session(session_id=self.session_dir.name)

    @property
    def session(self) -> Session:
        """Get the current session."""
        return self._session

    def save(self):
        """Save session to file."""
        try:
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(self._session.to_dict(), f, indent=2)
        except IOError as e:
            print(f"Failed to save session data: {e}")

    def add_file(self, file_path: str, file_type: str):
        """
        Add a file to the session and save.

        Args:
            file_path: Path to the file
            file_type: File type (php, js, other)
        """
        if self._session.add_file(file_path, file_type):
            self.save()

    def get_files(self, file_type: Optional[str] = None) -> list[str]:
        """Get list of tracked file paths (delegates to Session)."""
        return self._session.get_files(file_type)

    def get_files_by_type(self) -> dict[str, list[str]]:
        """Get files grouped by type (delegates to Session)."""
        return self._session.get_all_files_grouped()

    def set_metadata(self, key: str, value):
        """Set a metadata value and save."""
        self._session.metadata[key] = value
        self.save()

    def get_metadata(self, key: str, default=None):
        """Get a metadata value."""
        return self._session.metadata.get(key, default)

    def clear(self):
        """Clear the session directory."""
        if self.session_dir.exists():
            try:
                shutil.rmtree(self.session_dir)
            except IOError:
                pass


def get_file_type(file_path: str) -> str:
    """
    Determine file type from extension.

    Returns: 'php', 'js', or 'other'
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".php":
        return "php"
    elif ext in [".js", ".ts", ".tsx", ".jsx", ".vue"]:
        return "js"
    else:
        return "other"
