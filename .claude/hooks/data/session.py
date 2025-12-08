"""Session dataclass for representing a Claude Code session."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from .tracked_file import TrackedFile


@dataclass
class Session:
    """
    Represents a Claude Code session with typed fields.

    Contains all session state including tracked files and metadata.
    """

    session_id: str
    files: list[TrackedFile] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def short_id(self) -> str:
        """Get truncated session ID for display."""
        return self.session_id[:8] if self.session_id else "--------"

    def add_file(self, file_path: str, file_type: str) -> bool:
        """
        Add a file to the session's tracked files.

        Args:
            file_path: Path to the file (will be normalized)
            file_type: File type (php, js, other)

        Returns:
            True if file was added, False if already tracked
        """
        normalized_path = str(Path(file_path).resolve())

        # Check if already tracked
        if any(f.path == normalized_path for f in self.files):
            return False

        self.files.append(TrackedFile(path=normalized_path, file_type=file_type))
        return True

    def get_files(self, file_type: Optional[str] = None) -> list[str]:
        """
        Get list of tracked file paths.

        Args:
            file_type: Optional filter by file type (php, js, other)

        Returns:
            List of file paths
        """
        if file_type:
            return [f.path for f in self.files if f.file_type == file_type]
        return [f.path for f in self.files]

    def get_files_by_type(self, file_type: str) -> list[str]:
        """
        Get files of a specific type.

        Args:
            file_type: The file type to filter by (php, js, other)

        Returns:
            List of file paths matching the type
        """
        return [f.path for f in self.files if f.file_type == file_type]

    def get_all_files_grouped(self) -> dict[str, list[str]]:
        """
        Get all files grouped by type.

        Returns:
            Dict with type keys (php, js, other) and file path lists
        """
        result: dict[str, list[str]] = {"php": [], "js": [], "other": []}

        for tracked_file in self.files:
            if tracked_file.file_type in result:
                result[tracked_file.file_type].append(tracked_file.path)
            else:
                result["other"].append(tracked_file.path)

        return result

    def get_tracked_files(self, file_type: Optional[str] = None) -> list[TrackedFile]:
        """
        Get TrackedFile objects (with full metadata).

        Args:
            file_type: Optional filter by file type

        Returns:
            List of TrackedFile objects
        """
        if file_type:
            return [f for f in self.files if f.file_type == file_type]
        return self.files.copy()

    @property
    def file_count(self) -> int:
        """Get total number of tracked files."""
        return len(self.files)

    @property
    def php_files(self) -> list[str]:
        """Get PHP file paths."""
        return self.get_files_by_type("php")

    @property
    def js_files(self) -> list[str]:
        """Get JS/TS/Vue file paths."""
        return self.get_files_by_type("js")

    def to_dict(self) -> dict:
        """Convert session to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "files": [
                {"path": f.path, "type": f.file_type, "added_at": f.added_at}
                for f in self.files
            ],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Create Session from dictionary."""
        files = [
            TrackedFile(
                path=f["path"],
                file_type=f.get("type", "other"),
                added_at=f.get("added_at", datetime.now().isoformat()),
            )
            for f in data.get("files", [])
        ]

        return cls(
            session_id=data.get("session_id", ""),
            files=files,
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", datetime.now().isoformat()),
        )
