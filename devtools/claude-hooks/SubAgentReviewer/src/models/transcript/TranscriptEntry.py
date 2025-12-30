"""
Data class representing a single entry (line) from the transcript JSONL.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .ToolCall import ToolCall


@dataclass
class TranscriptEntry:
    """
    Represents a single line from the agent transcript JSONL file.

    Each line in the transcript is either:
    - A user message (initial prompt or tool results)
    - An assistant message (text response or tool calls)

    Key fields:
    - uuid: Unique identifier for this entry
    - parentUuid: Links to parent message (null for root/initial prompt)
    - type: "user" or "assistant"
    - message: The actual message content
    - agentId: The agent instance ID
    - sessionId: The session ID
    - timestamp: When this entry was created
    """

    uuid: str
    parent_uuid: str | None
    entry_type: str  # "user" or "assistant"
    agent_id: str
    session_id: str
    timestamp: datetime | None
    message_role: str  # "user" or "assistant"
    message_content: list[dict[str, Any]]
    raw_data: dict[str, Any]

    # Extracted data
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TranscriptEntry":
        """
        Parse a transcript entry from a dictionary.

        Args:
            data: Raw JSON data from one line of the transcript

        Returns:
            Parsed TranscriptEntry instance
        """
        message = data.get("message", {})

        # Handle both string and list content
        content = message.get("content", [])
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]

        # Parse timestamp
        timestamp = None
        if ts := data.get("timestamp"):
            try:
                timestamp = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        entry = cls(
            uuid=data.get("uuid", ""),
            parent_uuid=data.get("parentUuid"),
            entry_type=data.get("type", ""),
            agent_id=data.get("agentId", ""),
            session_id=data.get("sessionId", ""),
            timestamp=timestamp,
            message_role=message.get("role", ""),
            message_content=content,
            raw_data=data,
        )

        # Extract tool calls and results
        entry._extract_tool_data()

        return entry

    def _extract_tool_data(self) -> None:
        """Extract tool calls and results from message content."""
        for block in self.message_content:
            block_type = block.get("type", "")

            if block_type == "tool_use":
                self.tool_calls.append(ToolCall.from_dict(block))
            elif block_type == "tool_result":
                self.tool_results.append(block)

    @property
    def is_user(self) -> bool:
        """Check if this is a user entry."""
        return self.entry_type == "user"

    @property
    def is_assistant(self) -> bool:
        """Check if this is an assistant entry."""
        return self.entry_type == "assistant"

    @property
    def is_initial_prompt(self) -> bool:
        """Check if this is the initial prompt (root message)."""
        return self.is_user and self.parent_uuid is None

    @property
    def has_tool_calls(self) -> bool:
        """Check if this entry contains tool calls."""
        return len(self.tool_calls) > 0

    @property
    def has_tool_results(self) -> bool:
        """Check if this entry contains tool results."""
        return len(self.tool_results) > 0

    @property
    def file_modifying_tool_calls(self) -> list[ToolCall]:
        """Get only the tool calls that modify files."""
        return [tc for tc in self.tool_calls if tc.is_file_modifying]

    @property
    def initial_prompt_text(self) -> str | None:
        """
        Get the initial prompt text if this is the initial prompt entry.

        Returns:
            The prompt text, or None if not an initial prompt
        """
        if not self.is_initial_prompt:
            return None

        # Look for text content
        for block in self.message_content:
            if block.get("type") == "text":
                return block.get("text", "")
            # Sometimes content is just a string at the message level
            if isinstance(block, str):
                return block

        # Fallback: check if content was a string
        content = self.raw_data.get("message", {}).get("content")
        if isinstance(content, str):
            return content

        return None

    def __str__(self) -> str:
        tools = len(self.tool_calls)
        return f"TranscriptEntry({self.entry_type}, tools={tools})"
