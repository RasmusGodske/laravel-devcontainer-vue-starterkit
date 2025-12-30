"""
Formatter for generating review.md files.
"""

from dataclasses import dataclass
from datetime import datetime

from .ReviewerService import ReviewResult


@dataclass
class ReviewContext:
    """
    Context information for formatting a review.

    Collects all the information needed to generate a comprehensive review.md.
    """

    session_id: str
    agent_id: str
    agent_type: str
    review_number: int
    files_reviewed: list[str]
    original_task: str
    result: ReviewResult
    duration_ms: int
    timestamp: datetime | None = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ReviewMarkdownFormatter:
    """
    Formats review results as markdown.

    Generates comprehensive review.md files with all relevant context
    for debugging and transparency.

    Example:
        formatter = ReviewMarkdownFormatter()
        context = ReviewContext(
            session_id="abc-123",
            agent_id="e4d687e4",
            agent_type="backend-engineer",
            review_number=1,
            files_reviewed=["app/Models/User.php"],
            original_task="Add user model",
            result=ReviewResult(passed=False, feedback="Missing validation"),
            duration_ms=1500,
        )
        markdown = formatter.format(context)
    """

    def format(self, context: ReviewContext) -> str:
        """
        Format a review context as markdown.

        Args:
            context: The review context with all information

        Returns:
            Formatted markdown string
        """
        sections = [
            self._format_header(context),
            self._format_metadata(context),
            self._format_files(context),
            self._format_task(context),
            self._format_result(context),
        ]

        return "\n".join(sections)

    def _format_header(self, context: ReviewContext) -> str:
        """Format the header section."""
        status = "Passed" if context.result.passed else "Blocked"
        return f"# Review #{context.review_number}: {status}\n"

    def _format_metadata(self, context: ReviewContext) -> str:
        """Format the metadata section."""
        ts = context.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            "## Metadata\n",
            f"- **Timestamp:** {ts}",
            f"- **Session:** `{context.session_id}`",
            f"- **Agent:** `{context.agent_type}` (`{context.agent_id}`)",
            f"- **Duration:** {context.duration_ms}ms",
            "",
        ]
        return "\n".join(lines)

    def _format_files(self, context: ReviewContext) -> str:
        """Format the files section."""
        if not context.files_reviewed:
            return "## Files Reviewed\n\nNo files.\n"

        lines = [
            "## Files Reviewed\n",
        ]
        for f in context.files_reviewed:
            lines.append(f"- `{f}`")
        lines.append("")

        return "\n".join(lines)

    def _format_task(self, context: ReviewContext) -> str:
        """Format the original task section."""
        if not context.original_task:
            return ""

        # Truncate very long tasks
        task = context.original_task
        if len(task) > 2000:
            task = task[:2000] + "\n\n... (truncated)"

        lines = [
            "## Original Task\n",
            "```",
            task,
            "```",
            "",
        ]
        return "\n".join(lines)

    def _format_result(self, context: ReviewContext) -> str:
        """Format the result section."""
        lines = ["## Result\n"]

        if context.result.passed:
            lines.append("**Status:** Passed\n")
            if context.result.feedback:
                lines.append(context.result.feedback)
        else:
            lines.append("**Status:** Blocked\n")
            lines.append("### Feedback\n")
            lines.append(context.result.feedback)

        lines.append("")
        return "\n".join(lines)
