"""
Session manager for code reviews.
"""

import json
import secrets
from datetime import datetime
from pathlib import Path

from ..loggers import CodeReviewLogger
from ..models import CodeReviewSession


class CodeReviewSessionManager:
    """
    Manages code review sessions.

    Handles session ID generation, directory creation, and session persistence.

    Example:
        manager = CodeReviewSessionManager(
            sessions_path=Path("devtools/code-reviewer/sessions")
        )

        # Auto-generate session ID
        session, logger = manager.create_session()

        # Or use provided session ID
        session, logger = manager.create_session(session_id="my-session")
    """

    def __init__(self, sessions_path: Path) -> None:
        """
        Initialize the session manager.

        Args:
            sessions_path: Base path for storing sessions
        """
        self._sessions_path = sessions_path

    def generate_session_id(self) -> str:
        """
        Generate a short, unique session ID.

        Format: review-YYYYMMDD-XXXXXX
        Example: review-20251210-a1b2c3
        """
        date_part = datetime.now().strftime("%Y%m%d")
        random_part = secrets.token_hex(3)  # 6 hex chars
        return f"review-{date_part}-{random_part}"

    def create_session(
        self,
        session_id: str | None = None,
        verbose: bool = False,
        git_branch: str | None = None,
        git_commit: str | None = None,
    ) -> tuple[CodeReviewSession, CodeReviewLogger]:
        """
        Create a new session with its logger.

        Args:
            session_id: Optional session ID (auto-generated if not provided)
            verbose: If True, logger also outputs to stderr
            git_branch: Current git branch
            git_commit: Current git commit hash

        Returns:
            Tuple of (session, logger)
        """
        if session_id is None:
            session_id = self.generate_session_id()

        session = CodeReviewSession(
            session_id=session_id,
            base_path=self._sessions_path,
            git_branch=git_branch,
            git_commit=git_commit,
        )

        # Ensure session directory exists
        session.session_path.mkdir(parents=True, exist_ok=True)

        # Create logger for this session
        logger = CodeReviewLogger(
            session_id=session_id,
            log_path=session.log_path,
            verbose=verbose,
        )

        return session, logger

    def load_session(self, session_id: str) -> CodeReviewSession | None:
        """
        Load an existing session.

        Args:
            session_id: The session ID to load

        Returns:
            The session, or None if not found
        """
        session_path = self._sessions_path / session_id
        metadata_path = session_path / "session.json"

        if not metadata_path.exists():
            return None

        with open(metadata_path, encoding="utf-8") as f:
            data = json.load(f)

        return CodeReviewSession.from_dict(data, self._sessions_path)

    def save_session(self, session: CodeReviewSession) -> None:
        """
        Save session metadata.

        Args:
            session: The session to save
        """
        session.session_path.mkdir(parents=True, exist_ok=True)
        metadata_path = session.session_path / "session.json"

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, indent=2)
