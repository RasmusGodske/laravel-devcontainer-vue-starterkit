"""
Data class for parsing Claude Code hook input.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class HookInput:
    """
    Parsed hook input from Claude Code.

    SubagentStart hook provides:
    ```json
    {
      "session_id": "...",
      "transcript_path": "~/.claude/projects/.../session.jsonl",
      "cwd": "/home/vscode/project",
      "hook_event_name": "SubagentStart",
      "agent_id": "64fc4031",
      "agent_type": "backend-engineer"
    }
    ```

    SubagentStop hook provides:
    ```json
    {
      "session_id": "...",
      "transcript_path": "~/.claude/projects/.../session.jsonl",
      "cwd": "/home/vscode/project",
      "permission_mode": "default",
      "hook_event_name": "SubagentStop",
      "stop_hook_active": false,
      "agent_id": "64fc4031",
      "agent_transcript_path": "~/.claude/projects/.../agent-64fc4031.jsonl"
    }
    ```
    """

    session_id: str
    transcript_path: Path | None
    hook_event_name: str
    cwd: Path | None

    # Agent fields
    agent_id: str | None
    agent_type: str | None  # Only in SubagentStart
    agent_transcript_path: Path | None  # Only in SubagentStop

    # SubagentStop specific
    stop_hook_active: bool
    permission_mode: str

    raw_data: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HookInput":
        """
        Parse hook input from a dictionary.

        Args:
            data: Raw JSON data from stdin

        Returns:
            Parsed HookInput instance
        """
        transcript_path = data.get("transcript_path")
        if transcript_path:
            transcript_path = Path(transcript_path).expanduser()

        agent_transcript_path = data.get("agent_transcript_path")
        if agent_transcript_path:
            agent_transcript_path = Path(agent_transcript_path).expanduser()

        cwd = data.get("cwd")
        if cwd:
            cwd = Path(cwd)

        return cls(
            session_id=data.get("session_id", "unknown"),
            transcript_path=transcript_path,
            hook_event_name=data.get("hook_event_name", "unknown"),
            cwd=cwd,
            agent_id=data.get("agent_id"),
            agent_type=data.get("agent_type"),
            agent_transcript_path=agent_transcript_path,
            stop_hook_active=data.get("stop_hook_active", False),
            permission_mode=data.get("permission_mode", "default"),
            raw_data=data,
        )

    @property
    def is_stop_event(self) -> bool:
        """Check if this is a SubagentStop event."""
        return self.hook_event_name == "SubagentStop"

    @property
    def is_start_event(self) -> bool:
        """Check if this is a SubagentStart event."""
        return self.hook_event_name == "SubagentStart"

    @property
    def has_transcript(self) -> bool:
        """Check if a transcript path was provided."""
        return self.transcript_path is not None

    @property
    def transcript_exists(self) -> bool:
        """Check if the transcript file exists."""
        return self.has_transcript and self.transcript_path.exists()

    @property
    def transcript_dir(self) -> Path | None:
        """Get the directory containing the transcript."""
        if self.transcript_path:
            return self.transcript_path.parent
        return None

    @property
    def has_agent_id(self) -> bool:
        """Check if an agent ID was provided."""
        return self.agent_id is not None

    @property
    def has_agent_type(self) -> bool:
        """Check if an agent type was provided (SubagentStart only)."""
        return self.agent_type is not None

    @property
    def has_agent_transcript(self) -> bool:
        """Check if an agent transcript path was provided (SubagentStop only)."""
        return self.agent_transcript_path is not None

    @property
    def agent_transcript_exists(self) -> bool:
        """Check if the agent transcript file exists."""
        return self.has_agent_transcript and self.agent_transcript_path.exists()

    def __str__(self) -> str:
        return (
            f"HookInput(session={self.session_id}, "
            f"event={self.hook_event_name}, "
            f"agent={self.agent_id})"
        )
