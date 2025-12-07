#!/usr/bin/env python3
"""
Session file tracker for Claude Code hooks.

Tracks which files were modified during a Claude session by storing
file paths in a session-specific JSON file.

Usage:
    from session_tracker import SessionTracker

    tracker = SessionTracker(session_id)
    tracker.add_file("/path/to/file.php")
    files = tracker.get_files()
    tracker.clear()  # Clean up after end-of-turn check
"""

import json
import os
from pathlib import Path
from typing import Optional


class SessionTracker:
    """Tracks files modified during a Claude session."""

    def __init__(self, session_id: str, base_dir: Optional[str] = None):
        """
        Initialize the session tracker.

        Args:
            session_id: The Claude session ID
            base_dir: Base directory for sessions (defaults to .claude/sessions)
        """
        self.session_id = session_id

        if base_dir is None:
            # Default to .claude/sessions relative to hooks directory
            hooks_dir = Path(__file__).parent
            sessions_base = hooks_dir.parent / "sessions"
        else:
            sessions_base = Path(base_dir)

        # Each session gets its own directory
        self.session_dir = sessions_base / session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)

        self.session_file = self.session_dir / "files.json"

    def _load_data(self) -> dict:
        """Load session data from file."""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"files": [], "metadata": {}}
        return {"files": [], "metadata": {}}

    def _save_data(self, data: dict):
        """Save session data to file."""
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Failed to save session data: {e}")

    def add_file(self, file_path: str, file_type: Optional[str] = None):
        """
        Add a file to the session's modified files list.

        Args:
            file_path: Path to the file (will be normalized)
            file_type: Optional file type (php, js, etc.)
        """
        data = self._load_data()

        # Normalize path and avoid duplicates
        normalized_path = str(Path(file_path).resolve())

        # Check if already tracked
        existing_paths = [f["path"] for f in data["files"]]
        if normalized_path not in existing_paths:
            entry = {"path": normalized_path}
            if file_type:
                entry["type"] = file_type
            data["files"].append(entry)
            self._save_data(data)

    def get_files(self, file_type: Optional[str] = None) -> list[str]:
        """
        Get list of modified files.

        Args:
            file_type: Optional filter by file type (php, js, etc.)

        Returns:
            List of file paths
        """
        data = self._load_data()

        files = data.get("files", [])

        if file_type:
            files = [f for f in files if f.get("type") == file_type]

        return [f["path"] for f in files]

    def get_files_by_type(self) -> dict[str, list[str]]:
        """
        Get files grouped by type.

        Returns:
            Dict with type keys (php, js, other) and file path lists
        """
        data = self._load_data()
        result = {"php": [], "js": [], "other": []}

        for entry in data.get("files", []):
            file_type = entry.get("type", "other")
            if file_type in result:
                result[file_type].append(entry["path"])
            else:
                result["other"].append(entry["path"])

        return result

    def clear(self):
        """Clear the session directory (call after successful end-of-turn check)."""
        import shutil
        if self.session_dir.exists():
            try:
                shutil.rmtree(self.session_dir)
            except IOError:
                pass

    def set_metadata(self, key: str, value):
        """Set a metadata value for this session."""
        data = self._load_data()
        data["metadata"][key] = value
        self._save_data(data)

    def get_metadata(self, key: str, default=None):
        """Get a metadata value for this session."""
        data = self._load_data()
        return data.get("metadata", {}).get(key, default)


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
