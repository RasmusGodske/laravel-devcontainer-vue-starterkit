"""
Data class representing a file change extracted from the transcript.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class FileChangeAction(Enum):
    """The type of file modification."""

    CREATED = "created"
    EDITED = "edited"
    UNKNOWN = "unknown"


@dataclass
class FileChange:
    """
    Represents a file that was modified during the agent session.

    Extracted from tool calls like Edit, Write, or Serena symbol operations.

    Includes the full tool input for context:
    - Edit: old_string, new_string
    - Write: content
    - Serena tools: name_path, body, etc.
    """

    path: str
    action: FileChangeAction
    tool_name: str
    tool_call_id: str
    tool_input: dict[str, Any] = field(default_factory=dict)

    @property
    def absolute_path(self) -> Path:
        """Get the path as a Path object."""
        return Path(self.path)

    @property
    def filename(self) -> str:
        """Get just the filename."""
        return self.absolute_path.name

    @property
    def extension(self) -> str:
        """Get the file extension (without dot)."""
        return self.absolute_path.suffix.lstrip(".")

    @property
    def is_php(self) -> bool:
        """Check if this is a PHP file."""
        return self.extension == "php"

    @property
    def is_vue(self) -> bool:
        """Check if this is a Vue file."""
        return self.extension == "vue"

    @property
    def is_typescript(self) -> bool:
        """Check if this is a TypeScript file."""
        return self.extension in ("ts", "tsx")

    @property
    def is_javascript(self) -> bool:
        """Check if this is a JavaScript file."""
        return self.extension in ("js", "jsx")

    @property
    def is_frontend(self) -> bool:
        """Check if this is a frontend file."""
        return self.is_vue or self.is_typescript or self.is_javascript

    @property
    def is_backend(self) -> bool:
        """Check if this is a backend file."""
        return self.is_php

    def matches_pattern(self, pattern: str) -> bool:
        """
        Check if the file matches a glob-like pattern.

        Args:
            pattern: Simple pattern like "*.php" or "*.vue"

        Returns:
            True if the file matches the pattern
        """
        if pattern.startswith("*."):
            ext = pattern[2:]
            return self.extension == ext
        return pattern in self.path

    def matches_any_pattern(self, patterns: list[str]) -> bool:
        """Check if the file matches any of the given patterns."""
        return any(self.matches_pattern(p) for p in patterns)

    def __str__(self) -> str:
        return f"{self.path} ({self.action.value})"

    def __hash__(self) -> int:
        return hash(self.path)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FileChange):
            return False
        return self.path == other.path
