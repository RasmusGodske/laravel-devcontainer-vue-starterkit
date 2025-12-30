"""
Configuration options for code review.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# Type alias for MCP server configuration
McpServerConfig = dict[str, Any]


@dataclass
class CodeReviewOptions:
    """
    Configuration options for running a code review.

    Passed to CodeReviewService to configure the review behavior.
    """

    prompt_template_path: Path
    """Path to the prompt template file (.md)."""

    cwd: Path
    """Working directory for the review (where commands will run)."""

    allowed_tools: list[str] = field(
        default_factory=lambda: ["Read", "Bash", "Glob", "Grep"]
    )
    """Tools the reviewer agent can use."""

    max_turns: int = 15
    """Maximum number of tool calls the reviewer can make."""

    timeout_seconds: int = 90
    """Maximum time to wait for review completion."""

    mcp_servers: dict[str, McpServerConfig] = field(default_factory=dict)
    """MCP server configurations (e.g., {"serena": {"command": "...", "args": [...]}})."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "prompt_template_path": str(self.prompt_template_path),
            "cwd": str(self.cwd),
            "allowed_tools": self.allowed_tools,
            "max_turns": self.max_turns,
            "timeout_seconds": self.timeout_seconds,
            "mcp_servers": self.mcp_servers,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CodeReviewOptions":
        """Create from dictionary."""
        return cls(
            prompt_template_path=Path(data["prompt_template_path"]),
            cwd=Path(data.get("cwd", ".")),
            allowed_tools=data.get("allowed_tools", ["Read", "Bash", "Glob", "Grep"]),
            max_turns=data.get("max_turns", 15),
            timeout_seconds=data.get("timeout_seconds", 90),
            mcp_servers=data.get("mcp_servers", {}),
        )
