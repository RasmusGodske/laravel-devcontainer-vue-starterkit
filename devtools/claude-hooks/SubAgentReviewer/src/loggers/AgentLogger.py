"""
Agent-specific logger that writes to an agent's logs.txt file.
"""

from pathlib import Path

from .BaseLogger import BaseLogger


class AgentLogger(BaseLogger):
    """
    Logger for agent-specific events.

    Writes to: sessions/{session}/agents/{agent}/logs.txt

    Use this logger for:
    - Agent lifecycle events (start, stop)
    - Review triggers
    - File change detection
    - Agent-level errors

    Example:
        logger = AgentLogger(
            agent_dir=Path("./sessions/.../agents/2025-12-10T17-08-31-backend-engineer-abc123"),
            agent_id="abc123",
            agent_type="backend-engineer",
        )
        logger.info("Agent started")
        logger.info("Detected 5 file changes")
    """

    def __init__(
        self,
        agent_dir: Path,
        agent_id: str,
        agent_type: str,
        verbose: bool = False,
        also_stderr: bool = False,
    ):
        """
        Initialize the agent logger.

        Args:
            agent_dir: Path to the agent directory
            agent_id: The agent's unique ID
            agent_type: The agent type (e.g., "backend-engineer")
            verbose: If True, set DEBUG level; otherwise INFO
            also_stderr: If True, also log to stderr
        """
        super().__init__(verbose=verbose, also_stderr=also_stderr)
        self._agent_dir = agent_dir
        self._agent_id = agent_id
        self._agent_type = agent_type

    @property
    def log_path(self) -> Path:
        """Return the path to the agent log file."""
        return self._agent_dir / "logs.txt"

    @property
    def logger_name(self) -> str:
        """Return the logger name."""
        return f"subagent-reviewer.agent.{self._agent_id}"

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def log_agent_start(self) -> None:
        """Log agent start."""
        self.info(f"{'='*50}")
        self.info(f"Agent started: {self._agent_type}")
        self.info(f"Agent ID: {self._agent_id}")

    def log_agent_stop(self) -> None:
        """Log agent stop."""
        self.info(f"Agent stopped: {self._agent_id}")
        self.info(f"{'='*50}")

    def log_file_changes(self, file_paths: list[str]) -> None:
        """Log detected file changes."""
        self.info(f"File changes detected: {len(file_paths)}")
        for path in file_paths:
            self.info(f"  - {path}")

    def log_review_triggered(self, review_number: int) -> None:
        """Log that a review is being triggered."""
        self.info(f"Review #{review_number} triggered")

    def log_review_result(self, review_number: int, decision: str, reason: str) -> None:
        """Log review result."""
        self.info(f"Review #{review_number} result: {decision}")
        if decision == "block":
            self.info(f"Block reason: {reason[:200]}...")

    def log_skipped(self, reason: str) -> None:
        """Log that review was skipped."""
        self.info(f"Review skipped: {reason}")
