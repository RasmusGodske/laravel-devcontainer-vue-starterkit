"""
Result data from a code review.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CodeReviewResult:
    """
    Result from a code review operation.

    This is the primary return type from CodeReviewService.review().
    The CLI outputs this as JSON with `passed` and `feedback` fields.
    """

    has_issues: bool
    """Whether the review found blocking issues (True = blocked, False = passed)."""

    review_text: str
    """The full review output text from the reviewer agent."""

    started_at: datetime = field(default_factory=datetime.now)
    """When the review started."""

    completed_at: datetime = field(default_factory=datetime.now)
    """When the review completed."""

    duration_ms: int = 0
    """Total duration in milliseconds."""

    input_tokens: int = 0
    """Total input tokens used."""

    output_tokens: int = 0
    """Total output tokens used."""

    total_cost_usd: float | None = None
    """Total cost in USD (if available)."""

    @property
    def passed(self) -> bool:
        """Whether the review passed (no blocking issues)."""
        return not self.has_issues

    @property
    def feedback(self) -> str:
        """Feedback text (empty if passed, review text if blocked)."""
        return self.review_text if self.has_issues else ""

    @property
    def total_tokens(self) -> int:
        """Total tokens used (input + output)."""
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> dict[str, str | bool | int | float | None]:
        """
        Convert to dictionary for JSON output.

        Returns structure with review result and usage stats.
        """
        return {
            "passed": self.passed,
            "feedback": self.feedback,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "total_cost_usd": self.total_cost_usd,
        }

    @classmethod
    def error(cls, message: str) -> "CodeReviewResult":
        """
        Create a result for review errors.

        Errors don't block (passed=True) to avoid blocking on infrastructure issues.
        """
        return cls(
            has_issues=False,
            review_text=f"Review error: {message}",
        )

    @classmethod
    def empty(cls) -> "CodeReviewResult":
        """Create an empty result (no files to review)."""
        return cls(
            has_issues=False,
            review_text="",
        )
