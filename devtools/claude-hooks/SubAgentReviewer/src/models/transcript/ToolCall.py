"""
Data class representing a tool call from the transcript.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ToolCall:
    """
    Represents a tool_use content block from an assistant message.

    Example from transcript:
    ```json
    {
      "type": "tool_use",
      "id": "toolu_014cjemHByfyuNuXBGUkMceF",
      "name": "Edit",
      "input": {
        "file_path": "/home/vscode/project/app/Models/User.php",
        "old_string": "...",
        "new_string": "..."
      }
    }
    ```
    """

    id: str
    name: str
    input: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolCall":
        """Parse from a content block dictionary."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            input=data.get("input", {}),
        )

    @property
    def is_file_modifying(self) -> bool:
        """Check if this tool call modifies files."""
        return self.name in self.FILE_MODIFYING_TOOLS

    @property
    def file_path(self) -> str | None:
        """
        Extract the file path from the tool input.

        Different tools use different parameter names:
        - Edit, Write, Read: file_path
        - Serena tools: relative_path
        """
        # Standard Claude Code tools
        if "file_path" in self.input:
            return self.input["file_path"]

        # Serena MCP tools
        if "relative_path" in self.input:
            return self.input["relative_path"]

        return None

    # Tools that modify files
    FILE_MODIFYING_TOOLS: frozenset[str] = frozenset([
        # Standard Claude Code tools
        "Edit",
        "Write",
        "MultiEdit",
        # Serena MCP tools
        "mcp__serena__replace_symbol_body",
        "mcp__serena__insert_after_symbol",
        "mcp__serena__insert_before_symbol",
        "mcp__serena__rename_symbol",
    ])

    # Tools that read files (for context, not modification)
    FILE_READING_TOOLS: frozenset[str] = frozenset([
        "Read",
        "Glob",
        "Grep",
        "mcp__serena__find_symbol",
        "mcp__serena__get_symbols_overview",
        "mcp__serena__find_referencing_symbols",
    ])

    def __str__(self) -> str:
        path = self.file_path or "no-path"
        return f"ToolCall({self.name}, {path})"
