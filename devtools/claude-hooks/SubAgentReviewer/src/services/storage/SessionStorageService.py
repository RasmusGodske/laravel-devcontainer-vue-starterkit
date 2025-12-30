"""
Service for storing and retrieving session data.
"""

import json
from datetime import datetime
from pathlib import Path

from ...models.Session import AgentReview, Session, TrackedAgent
from .AgentPathResolver import AgentPathResolver
from .SessionPathResolver import SessionPathResolver


class SessionStorageService:
    """
    Manages session and agent storage on disk.

    Directory structure:
    ```
    sessions/
    └── {timestamp}-{session_id}/
        ├── session.json
        └── agents/
            └── {timestamp}-{agent_type}-{agent_id}/
                ├── logs.txt
                └── reviews/
                    └── {review_number}/
                        ├── review.md
                        ├── file-changes.json
                        └── logs.txt
    ```

    Example usage:
        storage = SessionStorageService(sessions_dir=Path("./sessions"))

        # On SubagentStart
        storage.track_agent_start(session_id, agent_id, agent_type, transcript_path)

        # On SubagentStop
        session, agent = storage.track_agent_stop(session_id, agent_id, transcript_path)
        agent_dir = storage.get_agent_dir(session_id, agent_id, agent.agent_type)

        # For reviews
        review_dir = storage.create_review_dir(session_id, agent_id)
    """

    SESSION_FILE = "session.json"

    def __init__(self, sessions_dir: Path):
        """
        Initialize the storage service.

        Args:
            sessions_dir: Base directory for session storage
        """
        self._sessions_dir = sessions_dir
        self._session_resolver = SessionPathResolver(sessions_dir)
        # Agent resolvers are created per-session as needed
        self._agent_resolvers: dict[str, AgentPathResolver] = {}

    def _session_dir(self, session_id: str) -> Path:
        """Get the directory for a session (finds existing or creates new path)."""
        return self._session_resolver.resolve(session_id)

    def _session_file(self, session_id: str) -> Path:
        """Get the session.json file path for a session."""
        return self._session_dir(session_id) / self.SESSION_FILE

    def _get_agent_resolver(self, session_id: str) -> AgentPathResolver:
        """
        Get or create an AgentPathResolver for a session.

        Args:
            session_id: The session ID

        Returns:
            AgentPathResolver for the session
        """
        if session_id not in self._agent_resolvers:
            session_dir = self._session_dir(session_id)
            self._agent_resolvers[session_id] = AgentPathResolver(session_dir)
        return self._agent_resolvers[session_id]

    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists."""
        existing = self._session_resolver.find(session_id)
        if existing is None:
            return False
        return (existing / self.SESSION_FILE).exists()

    def load_session(self, session_id: str) -> Session | None:
        """
        Load a session from disk.

        Args:
            session_id: The session ID

        Returns:
            The Session, or None if not found
        """
        session_file = self._session_file(session_id)
        if not session_file.exists():
            return None

        try:
            with open(session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Session.from_dict(data)
        except (json.JSONDecodeError, OSError):
            return None

    def save_session(self, session: Session) -> None:
        """
        Save a session to disk.

        Args:
            session: The Session to save
        """
        session_dir = self._session_dir(session.session_id)
        session_dir.mkdir(parents=True, exist_ok=True)

        session_file = self._session_file(session.session_id)
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, indent=2)

    def get_or_create_session(
        self,
        session_id: str,
        transcript_path: str = "",
        git_branch: str | None = None,
        git_commit: str | None = None,
    ) -> Session:
        """
        Get an existing session or create a new one.

        Args:
            session_id: The session ID
            transcript_path: Path to the main transcript (for new sessions)
            git_branch: Current git branch (for new sessions)
            git_commit: Current git commit hash (for new sessions)

        Returns:
            The Session (loaded or newly created)
        """
        session = self.load_session(session_id)
        if session is not None:
            return session

        from datetime import datetime
        return Session(
            session_id=session_id,
            started_at=datetime.now().isoformat(),
            transcript_path=transcript_path,
            git_branch=git_branch,
            git_commit=git_commit,
        )

    def track_agent_start(
        self,
        session_id: str,
        agent_id: str,
        agent_type: str,
        transcript_path: str = "",
        git_branch: str | None = None,
        git_commit: str | None = None,
        create_directory: bool = False,
    ) -> tuple[Session, Path | None]:
        """
        Track an agent starting (called from SubagentStart hook).

        Optionally creates the agent directory for logging.

        Args:
            session_id: The session ID
            agent_id: The agent's unique ID
            agent_type: The agent type (e.g., "backend-engineer")
            transcript_path: Path to the main transcript
            git_branch: Current git branch
            git_commit: Current git commit hash
            create_directory: If True, create agent directory on disk

        Returns:
            Tuple of (Session, agent_dir Path or None)
        """
        session = self.get_or_create_session(
            session_id,
            transcript_path,
            git_branch=git_branch,
            git_commit=git_commit,
        )
        session.add_agent(agent_id, agent_type)
        self.save_session(session)

        # Only create agent directory if requested (for agents that will be reviewed)
        agent_dir: Path | None = None
        if create_directory:
            agent_resolver = self._get_agent_resolver(session_id)
            agent_dir = agent_resolver.resolve(agent_id, agent_type)
            agent_dir.mkdir(parents=True, exist_ok=True)

        return session, agent_dir

    def track_agent_stop(
        self,
        session_id: str,
        agent_id: str,
        agent_transcript_path: str | None = None,
    ) -> tuple[Session | None, TrackedAgent | None, Path | None]:
        """
        Track an agent stopping (called from SubagentStop hook).

        Args:
            session_id: The session ID
            agent_id: The agent's unique ID
            agent_transcript_path: Path to the agent's transcript

        Returns:
            Tuple of (Session, TrackedAgent, agent_dir), or (None, None, None) if not found
        """
        session = self.load_session(session_id)
        if session is None:
            return None, None, None

        agent = session.end_agent(agent_id, agent_transcript_path)
        if agent is not None:
            self.save_session(session)

        # Get agent directory
        agent_resolver = self._get_agent_resolver(session_id)
        agent_dir = agent_resolver.find(agent_id)

        return session, agent, agent_dir

    def get_agent_type(self, session_id: str, agent_id: str) -> str | None:
        """
        Look up the agent type for a given agent ID.

        This is the key method for SubagentStop to determine if an agent
        should be reviewed.

        Args:
            session_id: The session ID
            agent_id: The agent's unique ID

        Returns:
            The agent type, or None if not found
        """
        session = self.load_session(session_id)
        if session is None:
            return None
        return session.get_agent_type(agent_id)

    def start_agent_review(
        self,
        session_id: str,
        agent_id: str,
    ) -> AgentReview | None:
        """
        Start a new review for an agent.

        Args:
            session_id: The session ID
            agent_id: The agent's unique ID

        Returns:
            The created AgentReview, or None if agent not found
        """
        session = self.load_session(session_id)
        if session is None:
            return None

        review = session.start_agent_review(agent_id)
        if review:
            self.save_session(session)
        return review

    def end_agent_review(
        self,
        session_id: str,
        agent_id: str,
        passed: bool,
        input_tokens: int = 0,
        output_tokens: int = 0,
        total_cost_usd: float | None = None,
    ) -> AgentReview | None:
        """
        End the current review for an agent.

        Args:
            session_id: The session ID
            agent_id: The agent's unique ID
            passed: True if review passed, False if blocked
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            total_cost_usd: Total cost in USD

        Returns:
            The updated AgentReview, or None if agent not found
        """
        session = self.load_session(session_id)
        if session is None:
            return None

        review = session.end_agent_review(
            agent_id=agent_id,
            passed=passed,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_cost_usd=total_cost_usd,
        )
        if review:
            self.save_session(session)
        return review

    def get_agent_review_count(
        self,
        session_id: str,
        agent_id: str,
    ) -> int:
        """
        Get the number of completed reviews for an agent.

        Args:
            session_id: The session ID
            agent_id: The agent's unique ID

        Returns:
            The number of completed reviews, or 0 if not found
        """
        session = self.load_session(session_id)
        if session is None:
            return 0
        return session.get_agent_review_count(agent_id)

    # =========================================================================
    # Agent Directory Methods
    # =========================================================================

    def get_agent_dir(self, session_id: str, agent_id: str) -> Path | None:
        """
        Get the directory for an agent.

        Args:
            session_id: The session ID
            agent_id: The agent ID

        Returns:
            Path to the agent directory, or None if not found
        """
        agent_resolver = self._get_agent_resolver(session_id)
        return agent_resolver.find(agent_id)

    def get_agent_log_path(self, session_id: str, agent_id: str) -> Path | None:
        """
        Get the log file path for an agent.

        Args:
            session_id: The session ID
            agent_id: The agent ID

        Returns:
            Path to logs.txt, or None if agent not found
        """
        agent_resolver = self._get_agent_resolver(session_id)
        return agent_resolver.agent_log(agent_id)

    # =========================================================================
    # Review Directory Methods
    # =========================================================================

    def create_review_dir(self, session_id: str, agent_id: str) -> tuple[Path, int]:
        """
        Create a new review directory for an agent.

        Args:
            session_id: The session ID
            agent_id: The agent ID

        Returns:
            Tuple of (review_dir Path, review_number)

        Raises:
            ValueError: If agent directory not found
        """
        agent_resolver = self._get_agent_resolver(session_id)
        agent_dir = agent_resolver.find(agent_id)

        if agent_dir is None:
            raise ValueError(f"Agent directory not found for {agent_id}")

        review_number = agent_resolver.next_review_number(agent_id)
        review_dir = agent_dir / "reviews" / str(review_number)
        review_dir.mkdir(parents=True, exist_ok=True)

        return review_dir, review_number

    def get_review_paths(
        self,
        session_id: str,
        agent_id: str,
        review_number: int,
    ) -> dict[str, Path] | None:
        """
        Get all file paths for a review.

        Args:
            session_id: The session ID
            agent_id: The agent ID
            review_number: The review number

        Returns:
            Dict with keys: 'dir', 'markdown', 'file_changes', 'log'
            Or None if agent not found
        """
        agent_resolver = self._get_agent_resolver(session_id)
        review_dir = agent_resolver.review_dir(agent_id, review_number)

        if review_dir is None:
            return None

        return {
            "dir": review_dir,
            "markdown": review_dir / "review.md",
            "file_changes": review_dir / "file-changes.json",
            "log": review_dir / "logs.txt",
        }

    # =========================================================================
    # Cleanup
    # =========================================================================

    def cleanup_old_sessions(
        self,
        max_age_days: int = 7,
        max_sessions: int = 100,
    ) -> int:
        """
        Clean up old session directories.

        Args:
            max_age_days: Maximum age of sessions to keep
            max_sessions: Maximum number of sessions to keep

        Returns:
            Number of sessions deleted
        """
        import shutil
        import time

        if not self._sessions_dir.exists():
            return 0

        sessions = list(self._sessions_dir.iterdir())
        if not sessions:
            return 0

        # Sort by name (oldest first due to timestamp prefix)
        sessions.sort(key=lambda p: p.name)

        deleted = 0
        cutoff_time = time.time() - (max_age_days * 86400)

        for session_dir in sessions:
            if not session_dir.is_dir():
                continue

            # Delete if too old or if we have too many
            should_delete = (
                session_dir.stat().st_mtime < cutoff_time
                or len(sessions) - deleted > max_sessions
            )

            if should_delete:
                try:
                    shutil.rmtree(session_dir)
                    deleted += 1
                except OSError:
                    pass

        return deleted
