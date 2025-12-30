"""
Utility for resolving session directory paths with sortable timestamps.

Directory naming: {timestamp}-{session_id}
Example: 2025-12-10T17-08-31-a4b024d3-e40f-4f27-9f56-deac2414269a
"""

from datetime import datetime
from pathlib import Path


class SessionPathResolver:
    """
    Resolves session directory paths with timestamp prefixes.

    Directory structure:
    ```
    sessions/
    └── 2025-12-10T17-08-31-a4b024d3-e40f-4f27-9f56-deac2414269a/
        └── session.json
    ```

    The timestamp prefix ensures directories are sortable by creation time.
    The session_id suffix allows lookup by session_id alone.

    Example:
        resolver = SessionPathResolver(sessions_dir=Path("./sessions"))

        # Find or create a session directory
        session_dir = resolver.resolve(session_id="abc-123")

        # Just find (don't create)
        session_dir = resolver.find(session_id="abc-123")
    """

    def __init__(self, sessions_dir: Path):
        """
        Initialize the resolver.

        Args:
            sessions_dir: Base directory containing all session directories
        """
        self._sessions_dir = sessions_dir

    def find(self, session_id: str) -> Path | None:
        """
        Find an existing session directory by session_id.

        Scans the sessions directory for any directory ending with -{session_id}.

        Args:
            session_id: The session ID to find

        Returns:
            Path to the session directory, or None if not found
        """
        if not self._sessions_dir.exists():
            return None

        # Look for directory with format: {timestamp}-{session_id}
        for entry in self._sessions_dir.iterdir():
            if not entry.is_dir():
                continue

            if entry.name.endswith(f"-{session_id}"):
                return entry

        return None

    def resolve(self, session_id: str, timestamp: datetime | None = None) -> Path:
        """
        Find existing session directory or create path for new one.

        If a directory for this session_id already exists, returns that path.
        Otherwise, returns a new path with timestamp prefix (directory not created).

        Args:
            session_id: The session ID
            timestamp: Timestamp for new directories (defaults to now)

        Returns:
            Path to the session directory (may or may not exist)
        """
        # Try to find existing
        existing = self.find(session_id)
        if existing is not None:
            return existing

        # Create new path with timestamp prefix
        if timestamp is None:
            timestamp = datetime.now()

        dir_name = self._format_dir_name(session_id, timestamp)
        return self._sessions_dir / dir_name

    def _format_dir_name(self, session_id: str, timestamp: datetime) -> str:
        """
        Format the directory name with timestamp prefix.

        Format: {YYYY-MM-DDTHH-MM-SS}-{session_id}

        Uses hyphens instead of colons in time to be filesystem-safe.

        Args:
            session_id: The session ID
            timestamp: The timestamp

        Returns:
            Formatted directory name
        """
        # Format: 2025-12-10T17-08-31 (no colons, filesystem-safe)
        ts_str = timestamp.strftime("%Y-%m-%dT%H-%M-%S")
        return f"{ts_str}-{session_id}"

    def list_sessions(self, limit: int | None = None) -> list[Path]:
        """
        List all session directories, sorted by name (most recent first).

        Because directories are prefixed with timestamps, sorting by name
        gives chronological order.

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of session directory paths, newest first
        """
        if not self._sessions_dir.exists():
            return []

        dirs = [
            entry
            for entry in self._sessions_dir.iterdir()
            if entry.is_dir()
        ]

        # Sort by name descending (newest first due to timestamp prefix)
        dirs.sort(key=lambda p: p.name, reverse=True)

        if limit is not None:
            dirs = dirs[:limit]

        return dirs

    def extract_session_id(self, session_dir: Path) -> str:
        """
        Extract the session_id from a directory name.

        Format: {timestamp}-{session_id} -> session_id

        Args:
            session_dir: Path to the session directory

        Returns:
            The session ID
        """
        dir_name = session_dir.name

        # Format: YYYY-MM-DDTHH-MM-SS-{session_id}
        # Timestamp is 19 chars + 1 separator = 20 chars prefix
        return dir_name[20:]
