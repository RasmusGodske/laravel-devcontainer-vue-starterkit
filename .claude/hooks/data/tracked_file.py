"""TrackedFile dataclass for representing tracked files in a session."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class TrackedFile:
    """Represents a file tracked during a session."""

    path: str
    file_type: str
    added_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def exists(self) -> bool:
        """Check if the file still exists on disk."""
        return Path(self.path).exists()

    @property
    def name(self) -> str:
        """Get the file name without path."""
        return Path(self.path).name

    @property
    def extension(self) -> str:
        """Get the file extension."""
        return Path(self.path).suffix.lower()
