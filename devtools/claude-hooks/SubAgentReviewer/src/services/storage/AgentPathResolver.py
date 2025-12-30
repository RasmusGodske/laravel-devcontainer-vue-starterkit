"""
Utility for resolving agent directory paths with sortable timestamps.

Directory naming: {timestamp}-{agent_type}-{agent_id}
Example: 2025-12-10T17-08-31-backend-engineer-e4d687e4
"""

from datetime import datetime
from pathlib import Path


class AgentPathResolver:
    """
    Resolves agent directory paths with timestamp prefixes.

    Directory structure:
    ```
    sessions/{timestamp}-{session_id}/
    └── agents/
        └── {timestamp}-{agent_type}-{agent_id}/
            ├── logs.txt
            └── reviews/
                └── {review_number}/
                    ├── review.md
                    ├── file-changes.json
                    └── logs.txt
    ```

    The timestamp prefix ensures directories are sortable by creation time.

    Example:
        resolver = AgentPathResolver(session_dir=Path("./sessions/2025-12-10T17-08-31-abc123"))

        # Find or create an agent directory
        agent_dir = resolver.resolve(agent_id="e4d687e4", agent_type="backend-engineer")

        # Get review directory
        review_dir = resolver.review_dir(agent_id="e4d687e4", review_number=1)
    """

    AGENTS_DIR = "agents"
    REVIEWS_DIR = "reviews"

    def __init__(self, session_dir: Path):
        """
        Initialize the resolver.

        Args:
            session_dir: The session directory containing agents
        """
        self._session_dir = session_dir
        self._agents_dir = session_dir / self.AGENTS_DIR

    @property
    def agents_dir(self) -> Path:
        """Get the agents directory."""
        return self._agents_dir

    def find(self, agent_id: str) -> Path | None:
        """
        Find an existing agent directory by agent_id.

        Scans the agents directory for any directory ending with -{agent_id}.

        Args:
            agent_id: The agent ID to find

        Returns:
            Path to the agent directory, or None if not found
        """
        if not self._agents_dir.exists():
            return None

        # Look for directory with format: {timestamp}-{agent_type}-{agent_id}
        for entry in self._agents_dir.iterdir():
            if not entry.is_dir():
                continue

            if entry.name.endswith(f"-{agent_id}"):
                return entry

        return None

    def resolve(
        self,
        agent_id: str,
        agent_type: str,
        timestamp: datetime | None = None,
    ) -> Path:
        """
        Find existing agent directory or create path for new one.

        If a directory for this agent_id already exists, returns that path.
        Otherwise, returns a new path with timestamp prefix (directory not created).

        Args:
            agent_id: The agent ID
            agent_type: The agent type (e.g., "backend-engineer")
            timestamp: Timestamp for new directories (defaults to now)

        Returns:
            Path to the agent directory (may or may not exist)
        """
        # Try to find existing
        existing = self.find(agent_id)
        if existing is not None:
            return existing

        # Create new path with timestamp prefix
        if timestamp is None:
            timestamp = datetime.now()

        dir_name = self._format_dir_name(agent_id, agent_type, timestamp)
        return self._agents_dir / dir_name

    def _format_dir_name(
        self,
        agent_id: str,
        agent_type: str,
        timestamp: datetime,
    ) -> str:
        """
        Format the directory name with timestamp prefix.

        Format: {YYYY-MM-DDTHH-MM-SS}-{agent_type}-{agent_id}

        Args:
            agent_id: The agent ID
            agent_type: The agent type
            timestamp: The timestamp

        Returns:
            Formatted directory name
        """
        ts_str = timestamp.strftime("%Y-%m-%dT%H-%M-%S")
        return f"{ts_str}-{agent_type}-{agent_id}"

    def list_agents(self, limit: int | None = None) -> list[Path]:
        """
        List all agent directories, sorted by name (most recent first).

        Args:
            limit: Maximum number of agents to return

        Returns:
            List of agent directory paths, newest first
        """
        if not self._agents_dir.exists():
            return []

        dirs = [
            entry
            for entry in self._agents_dir.iterdir()
            if entry.is_dir()
        ]

        # Sort by name descending (newest first due to timestamp prefix)
        dirs.sort(key=lambda p: p.name, reverse=True)

        if limit is not None:
            dirs = dirs[:limit]

        return dirs

    # =========================================================================
    # Review Paths
    # =========================================================================

    def reviews_dir(self, agent_id: str) -> Path | None:
        """
        Get the reviews directory for an agent.

        Args:
            agent_id: The agent ID

        Returns:
            Path to the reviews directory, or None if agent not found
        """
        agent_dir = self.find(agent_id)
        if agent_dir is None:
            return None
        return agent_dir / self.REVIEWS_DIR

    def review_dir(self, agent_id: str, review_number: int) -> Path | None:
        """
        Get a specific review directory for an agent.

        Args:
            agent_id: The agent ID
            review_number: The review number (1-indexed)

        Returns:
            Path to the review directory, or None if agent not found
        """
        reviews = self.reviews_dir(agent_id)
        if reviews is None:
            return None
        return reviews / str(review_number)

    def next_review_number(self, agent_id: str) -> int:
        """
        Get the next review number for an agent.

        Scans existing review directories and returns the next number.

        Args:
            agent_id: The agent ID

        Returns:
            The next review number (1 if no reviews exist)
        """
        reviews = self.reviews_dir(agent_id)
        if reviews is None or not reviews.exists():
            return 1

        existing = [
            int(d.name)
            for d in reviews.iterdir()
            if d.is_dir() and d.name.isdigit()
        ]

        if not existing:
            return 1

        return max(existing) + 1

    # =========================================================================
    # File Paths
    # =========================================================================

    def agent_log(self, agent_id: str) -> Path | None:
        """
        Get the log file path for an agent.

        Args:
            agent_id: The agent ID

        Returns:
            Path to logs.txt, or None if agent not found
        """
        agent_dir = self.find(agent_id)
        if agent_dir is None:
            return None
        return agent_dir / "logs.txt"

    def review_markdown(self, agent_id: str, review_number: int) -> Path | None:
        """
        Get the review.md file path for a review.

        Args:
            agent_id: The agent ID
            review_number: The review number

        Returns:
            Path to review.md, or None if agent not found
        """
        review = self.review_dir(agent_id, review_number)
        if review is None:
            return None
        return review / "review.md"

    def review_file_changes(self, agent_id: str, review_number: int) -> Path | None:
        """
        Get the file-changes.json file path for a review.

        Args:
            agent_id: The agent ID
            review_number: The review number

        Returns:
            Path to file-changes.json, or None if agent not found
        """
        review = self.review_dir(agent_id, review_number)
        if review is None:
            return None
        return review / "file-changes.json"

    def review_log(self, agent_id: str, review_number: int) -> Path | None:
        """
        Get the logs.txt file path for a review.

        Args:
            agent_id: The agent ID
            review_number: The review number

        Returns:
            Path to logs.txt, or None if agent not found
        """
        review = self.review_dir(agent_id, review_number)
        if review is None:
            return None
        return review / "logs.txt"

    # =========================================================================
    # Extraction
    # =========================================================================

    def extract_agent_id(self, agent_dir: Path) -> str:
        """
        Extract the agent_id from a directory name.

        Format: {timestamp}-{agent_type}-{agent_id} -> agent_id

        Args:
            agent_dir: Path to the agent directory

        Returns:
            The agent ID (last segment after final hyphen)
        """
        # agent_id is the last segment (after the last hyphen)
        # Format: 2025-12-10T17-08-31-backend-engineer-e4d687e4
        return agent_dir.name.rsplit("-", 1)[-1]

    def extract_agent_type(self, agent_dir: Path) -> str:
        """
        Extract the agent_type from a directory name.

        Format: {timestamp}-{agent_type}-{agent_id} -> agent_type

        Args:
            agent_dir: Path to the agent directory

        Returns:
            The agent type (middle segment)
        """
        dir_name = agent_dir.name
        # Remove timestamp prefix (20 chars: YYYY-MM-DDTHH-MM-SS-)
        without_timestamp = dir_name[20:]
        # Remove agent_id suffix (after last hyphen)
        agent_type = without_timestamp.rsplit("-", 1)[0]
        return agent_type
