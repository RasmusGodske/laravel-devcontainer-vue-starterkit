"""
Session tracking for code reviews.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class CodeReviewSession:
    """
    Tracks a code review session.

    A session groups related review operations and provides a directory
    for logs and artifacts. Sessions can be auto-generated or user-provided.

    Example session ID: "review-20251210-a1b2c3"
    """

    session_id: str
    """Unique session identifier."""

    base_path: Path
    """Base path for session storage (e.g., devtools/code-reviewer/sessions)."""

    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    """ISO timestamp when session was created."""

    review_input: str = ""
    """The raw input passed to the review (--files argument)."""

    git_branch: str | None = None
    """Git branch when review was run."""

    git_commit: str | None = None
    """Git commit hash (short) when review was run."""

    # Review result fields (populated after review completes)
    completed_at: str | None = None
    """ISO timestamp when review completed."""

    decision: str | None = None
    """Review decision: 'passed' or 'blocked'."""

    duration_ms: int = 0
    """Total duration in milliseconds."""

    input_tokens: int = 0
    """Total input tokens used."""

    output_tokens: int = 0
    """Total output tokens used."""

    total_cost_usd: float | None = None
    """Total cost in USD."""

    @property
    def session_path(self) -> Path:
        """Path to this session's directory."""
        return self.base_path / self.session_id

    @property
    def log_path(self) -> Path:
        """Path to the session log file."""
        return self.session_path / "log.txt"

    @property
    def total_tokens(self) -> int:
        """Total tokens used (input + output)."""
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "review_input": self.review_input,
            "git_branch": self.git_branch,
            "git_commit": self.git_commit,
            "completed_at": self.completed_at,
            "decision": self.decision,
            "duration_ms": self.duration_ms,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "total_cost_usd": self.total_cost_usd,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], base_path: Path) -> "CodeReviewSession":
        """Create from dictionary."""
        return cls(
            session_id=data["session_id"],
            base_path=base_path,
            created_at=data.get("created_at", datetime.now().isoformat()),
            review_input=data.get("review_input", ""),
            git_branch=data.get("git_branch"),
            git_commit=data.get("git_commit"),
            completed_at=data.get("completed_at"),
            decision=data.get("decision"),
            duration_ms=data.get("duration_ms", 0),
            input_tokens=data.get("input_tokens", 0),
            output_tokens=data.get("output_tokens", 0),
            total_cost_usd=data.get("total_cost_usd"),
        )
