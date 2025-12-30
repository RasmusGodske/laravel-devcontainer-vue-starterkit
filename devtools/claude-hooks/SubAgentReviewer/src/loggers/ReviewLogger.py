"""
Review-specific logger that writes to a review's logs.txt file.
"""

from pathlib import Path

from .BaseLogger import BaseLogger


class ReviewLogger(BaseLogger):
    """
    Logger for review-specific events.

    Writes to: sessions/{session}/agents/{agent}/reviews/{number}/logs.txt

    Use this logger for:
    - Review execution details
    - Reviewer tool invocation
    - Review output processing
    - Review decision details

    Example:
        logger = ReviewLogger(
            review_dir=Path("./sessions/.../agents/.../reviews/1"),
            review_number=1,
            agent_id="abc123",
        )
        logger.info("Starting backend review")
        logger.log_tool_invocation("backend-review", ["--files", "app/Models/User.php"])
    """

    def __init__(
        self,
        review_dir: Path,
        review_number: int,
        agent_id: str,
        verbose: bool = False,
        also_stderr: bool = False,
    ):
        """
        Initialize the review logger.

        Args:
            review_dir: Path to the review directory
            review_number: The review number (1-indexed)
            agent_id: The agent's unique ID
            verbose: If True, set DEBUG level; otherwise INFO
            also_stderr: If True, also log to stderr
        """
        super().__init__(verbose=verbose, also_stderr=also_stderr)
        self._review_dir = review_dir
        self._review_number = review_number
        self._agent_id = agent_id

    @property
    def log_path(self) -> Path:
        """Return the path to the review log file."""
        return self._review_dir / "logs.txt"

    @property
    def logger_name(self) -> str:
        """Return the logger name."""
        return f"subagent-reviewer.review.{self._agent_id}.{self._review_number}"

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def log_review_start(self, files_to_review: list[str]) -> None:
        """Log review start."""
        self.info(f"{'='*50}")
        self.info(f"Review #{self._review_number} started")
        self.info(f"Files to review: {len(files_to_review)}")
        for f in files_to_review:
            self.info(f"  - {f}")

    def log_tool_invocation(self, tool_name: str, args: list[str]) -> None:
        """Log reviewer tool invocation."""
        self.info(f"Invoking: {tool_name}")
        self.debug(f"Args: {args}")

    def log_tool_output(self, output: str, truncate: int = 1000) -> None:
        """Log reviewer tool output."""
        if len(output) > truncate:
            self.info(f"Tool output ({len(output)} chars, truncated):")
            self.info(output[:truncate] + "...")
        else:
            self.info(f"Tool output:")
            self.info(output)

    def log_tool_error(self, error: str) -> None:
        """Log reviewer tool error."""
        self.error(f"Tool error: {error}")

    def log_decision(self, decision: str, reason: str) -> None:
        """Log review decision."""
        self.info(f"Decision: {decision}")
        if reason:
            self.info(f"Reason: {reason[:500]}")

    def log_review_end(self, duration_ms: int) -> None:
        """Log review completion."""
        self.info(f"Review #{self._review_number} completed in {duration_ms}ms")
        self.info(f"{'='*50}")
