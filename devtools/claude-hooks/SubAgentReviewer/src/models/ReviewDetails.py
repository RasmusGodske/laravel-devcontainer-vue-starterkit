"""
Data class for review details stored as JSON.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ReviewFileChange:
    """A file change included in the review."""

    path: str
    action: str  # "created", "edited", etc.
    tool_name: str = ""
    tool_input: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "action": self.action,
            "tool_name": self.tool_name,
            "tool_input": self.tool_input,
        }


@dataclass
class ReviewDetails:
    """
    Details about a code review, saved as review-details.json.

    Contains all structured data about the review for programmatic access.
    """

    session_id: str
    agent_id: str
    agent_type: str
    review_number: int
    decision: str  # "allow" or "block"
    duration_ms: int
    file_changes: list[ReviewFileChange] = field(default_factory=list)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "review_number": self.review_number,
            "decision": self.decision,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
            "file_changes": [fc.to_dict() for fc in self.file_changes],
        }

    def save(self, review_dir: Path) -> Path:
        """
        Save to review-details.json in the given directory.

        Args:
            review_dir: The review directory

        Returns:
            Path to the saved file
        """
        path = review_dir / "review-details.json"
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        return path

    @classmethod
    def from_dict(cls, data: dict) -> "ReviewDetails":
        """Load from a dictionary."""
        file_changes = [
            ReviewFileChange(
                path=fc["path"],
                action=fc["action"],
                tool_name=fc.get("tool_name", ""),
                tool_input=fc.get("tool_input", {}),
            )
            for fc in data.get("file_changes", [])
        ]
        return cls(
            session_id=data.get("session_id", ""),
            agent_id=data.get("agent_id", ""),
            agent_type=data.get("agent_type", ""),
            review_number=data.get("review_number", 0),
            decision=data.get("decision", ""),
            duration_ms=data.get("duration_ms", 0),
            timestamp=data.get("timestamp", ""),
            file_changes=file_changes,
        )

    @classmethod
    def load(cls, review_dir: Path) -> "ReviewDetails":
        """
        Load from review-details.json in the given directory.

        Args:
            review_dir: The review directory

        Returns:
            Loaded ReviewDetails

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        path = review_dir / "review-details.json"
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)
