"""
Centralized path management for SubAgentReviewer.

Single source of truth for all paths used in the hook.
Supports configurable output directory for portability across projects.
"""

from pathlib import Path


class Paths:
    """
    Centralized path management for the subagent-reviewer hook.

    Provides consistent access to all important paths in the hook's
    directory structure. Supports configurable output directory.

    Default directory structure (output_dir not set):
    ```
    devtools/claude-hooks/SubAgentReviewer/
    ├── hook.log              # Global log
    ├── main.py
    ├── src/
    └── sessions/             # Default output location
        └── {session_id}/...
    ```

    With output_dir configured (e.g., "analytics/subagent-reviewer"):
    ```
    project_root/
    └── analytics/
        └── subagent-reviewer/
            └── sessions/
                └── {session_id}/...
    ```

    Example:
        # Default (sessions in tool directory)
        paths = Paths()

        # Custom output directory
        paths = Paths(output_dir="analytics/subagent-reviewer")
    """

    # Class-level base directory (can be overridden for testing)
    _base_dir: Path | None = None

    def __init__(
        self,
        base_dir: Path | None = None,
        output_dir: str | None = None,
    ):
        """
        Initialize paths with optional overrides.

        Args:
            base_dir: Optional base directory for the tool itself.
            output_dir: Optional output directory for sessions/logs.
                        Can be relative (resolved from project root) or absolute.
        """
        if base_dir is not None:
            self._instance_base_dir = base_dir
        else:
            self._instance_base_dir = self._get_default_base_dir()

        self._output_dir = self._resolve_output_dir(output_dir)

    def _resolve_output_dir(self, output_dir: str | None) -> Path:
        """
        Resolve the output directory path.

        Args:
            output_dir: Output directory string from config

        Returns:
            Resolved absolute path for output
        """
        if output_dir is None:
            # Default: use tool's own directory
            return self._instance_base_dir

        output_path = Path(output_dir)

        if output_path.is_absolute():
            return output_path
        else:
            # Relative paths are resolved from project root
            return self.project_root / output_path

    @classmethod
    def _get_default_base_dir(cls) -> Path:
        """Get the default base directory."""
        if cls._base_dir is not None:
            return cls._base_dir
        # src/Paths.py -> src -> SubAgentReviewer
        return Path(__file__).parent.parent

    @classmethod
    def set_base_dir(cls, path: Path) -> None:
        """Set the base directory (useful for testing)."""
        cls._base_dir = path

    @classmethod
    def reset_base_dir(cls) -> None:
        """Reset the base directory to the default."""
        cls._base_dir = None

    # =========================================================================
    # Base Directories
    # =========================================================================

    @property
    def base_dir(self) -> Path:
        """Get the SubAgentReviewer base directory (where the tool code lives)."""
        return self._instance_base_dir

    @property
    def output_dir(self) -> Path:
        """Get the output directory (where sessions/logs are stored)."""
        return self._output_dir

    @property
    def src_dir(self) -> Path:
        """Get the src directory."""
        return self._instance_base_dir / "src"

    @property
    def sessions_dir(self) -> Path:
        """Get the sessions directory (in output_dir)."""
        return self._output_dir / "sessions"

    # =========================================================================
    # Global Files
    # =========================================================================

    @property
    def global_log(self) -> Path:
        """Get the global hook.log file path."""
        return self._instance_base_dir / "hook.log"

    # =========================================================================
    # Project Paths
    # =========================================================================

    @property
    def project_root(self) -> Path:
        """
        Get the project root directory.

        SubAgentReviewer2 -> claude-hooks -> devtools -> project_root
        """
        return self._instance_base_dir.parent.parent.parent

    @property
    def devtools_dir(self) -> Path:
        """Get the devtools directory."""
        return self.project_root / "devtools"

    @property
    def claude_dir(self) -> Path:
        """Get the .claude directory in the project root."""
        return self.project_root / ".claude"

    # =========================================================================
    # Session Paths
    # =========================================================================

    def session_dir(self, session_id: str) -> Path:
        """
        Get the directory for a session.

        Args:
            session_id: The Claude Code session ID

        Returns:
            Path to the session directory
        """
        return self.sessions_dir / session_id

    def session_log(self, session_id: str) -> Path:
        """Get the log file path for a session."""
        return self.session_dir(session_id) / "session.log"

    # =========================================================================
    # Agent Paths
    # =========================================================================

    def agent_dir(self, session_id: str, agent_id: str) -> Path:
        """
        Get the directory for an agent instance.

        Args:
            session_id: The Claude Code session ID
            agent_id: The agent instance ID

        Returns:
            Path to the agent directory
        """
        return self.session_dir(session_id) / "agents" / agent_id

    def agent_metadata(self, session_id: str, agent_id: str) -> Path:
        """Get the metadata file path for an agent."""
        return self.agent_dir(session_id, agent_id) / "agent.json"

    # =========================================================================
    # Review Paths
    # =========================================================================

    def reviews_dir(self, session_id: str, agent_id: str) -> Path:
        """Get the reviews directory for an agent."""
        return self.agent_dir(session_id, agent_id) / "reviews"

    def review_dir(self, session_id: str, agent_id: str, review_id: str) -> Path:
        """
        Get the directory for a specific review.

        Args:
            session_id: The Claude Code session ID
            agent_id: The agent instance ID
            review_id: The review ID (typically a timestamp)

        Returns:
            Path to the review directory
        """
        return self.reviews_dir(session_id, agent_id) / review_id

    def review_markdown(
        self, session_id: str, agent_id: str, review_id: str
    ) -> Path:
        """Get the review.md file path."""
        return self.review_dir(session_id, agent_id, review_id) / "review.md"

    def review_log(self, session_id: str, agent_id: str, review_id: str) -> Path:
        """Get the review log file path."""
        return self.review_dir(session_id, agent_id, review_id) / "review.log"

    # =========================================================================
    # Tool Paths
    # =========================================================================

    def review_tool(self, tool_name: str) -> Path:
        """
        Get the path to a review tool.

        Args:
            tool_name: Name of the tool directory (e.g., "backend-review")

        Returns:
            Path to the tool's cli.py
        """
        return self.devtools_dir / tool_name / "cli.py"

    @property
    def backend_review_tool(self) -> Path:
        """Get path to the backend review tool."""
        return self.review_tool("backend-review")

    @property
    def frontend_review_tool(self) -> Path:
        """Get path to the frontend review tool."""
        return self.review_tool("frontend-review")
