"""
Service for running code reviews via the code-reviewer tool.
"""

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ReviewResult:
    """
    Result from the code-reviewer.

    Includes review decision, feedback, and usage statistics.
    """

    passed: bool
    feedback: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    total_cost_usd: float | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "ReviewResult":
        """Parse from JSON response."""
        return cls(
            passed=data.get("passed", True),
            feedback=data.get("feedback", ""),
            input_tokens=data.get("input_tokens", 0),
            output_tokens=data.get("output_tokens", 0),
            total_tokens=data.get("total_tokens", 0),
            total_cost_usd=data.get("total_cost_usd"),
        )

    @classmethod
    def error(cls, message: str) -> "ReviewResult":
        """Create an error result (allows agent to proceed)."""
        return cls(passed=True, feedback=f"Review error: {message}")


class ReviewerService:
    """
    Runs code reviews using the code-reviewer tool.

    This service is intentionally simple:
    - Takes files and task
    - Calls code-reviewer
    - Returns result without interpretation

    Example:
        service = ReviewerService(tool_path=Path("./devtools/code-reviewer/cli.py"))
        result = service.review(
            files=["app/Models/User.php", "app/Services/UserService.php"],
            original_task="Added user registration feature",
        )
        if not result.passed:
            # Block agent with result.feedback
    """

    def __init__(
        self,
        tool_path: Path,
        timeout_seconds: int = 90,
        project_dir: Path | None = None,
    ):
        """
        Initialize the reviewer service.

        Args:
            tool_path: Path to the code-reviewer cli.py
            timeout_seconds: Maximum time to wait for review
            project_dir: Project directory (for CLAUDE_PROJECT_DIR env var)
        """
        self._tool_path = tool_path
        self._timeout = timeout_seconds
        self._project_dir = project_dir

    def review(
        self,
        files: list[str],
        original_task: str = "",
    ) -> ReviewResult:
        """
        Run a code review on the given files.

        Args:
            files: List of file paths to review
            original_task: The original task/prompt (provides context)

        Returns:
            ReviewResult with passed status and feedback
        """
        if not files:
            return ReviewResult(passed=True, feedback="")

        if not self._tool_path.exists():
            return ReviewResult.error(f"Code reviewer not found: {self._tool_path}")

        # Format files as comma-separated string
        files_str = ", ".join(files)

        # Build command
        cmd = [
            sys.executable,
            str(self._tool_path),
            "--files", files_str,
            "--json",
        ]

        if original_task:
            cmd.extend(["--task", original_task])

        # Set up environment
        env = None
        if self._project_dir:
            import os
            env = os.environ.copy()
            env["CLAUDE_PROJECT_DIR"] = str(self._project_dir)

        # Run the review
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self._timeout,
                env=env,
            )
        except subprocess.TimeoutExpired:
            # On timeout, allow agent to proceed (don't block indefinitely)
            return ReviewResult.error(f"Review timed out after {self._timeout}s")
        except Exception as e:
            return ReviewResult.error(str(e))

        # Parse JSON output
        try:
            data = json.loads(result.stdout)
            return ReviewResult.from_dict(data)
        except json.JSONDecodeError:
            # If JSON parsing fails, check exit code
            if result.returncode == 0:
                return ReviewResult(passed=True, feedback="")
            else:
                # Return stderr or stdout as feedback
                feedback = result.stderr or result.stdout or "Review failed (unknown error)"
                return ReviewResult(passed=False, feedback=feedback)
