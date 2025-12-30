"""
Data class representing the analysis result of a transcript.
"""

from dataclasses import dataclass, field
from pathlib import Path

from .transcript import FileChange, TranscriptEntry


@dataclass
class TranscriptAnalysis:
    """
    Result of analyzing an agent transcript.

    Contains the extracted information needed for code review:
    - Initial prompt (the task the agent was given)
    - File changes (files created/edited)
    - Metadata (agent ID, session ID, etc.)
    """

    agent_id: str
    session_id: str
    transcript_path: Path
    initial_prompt: str
    file_changes: list[FileChange] = field(default_factory=list)
    entries: list[TranscriptEntry] = field(default_factory=list)

    @property
    def has_file_changes(self) -> bool:
        """Check if any files were modified."""
        return len(self.file_changes) > 0

    @property
    def file_change_count(self) -> int:
        """Get the number of file changes."""
        return len(self.file_changes)

    @property
    def entry_count(self) -> int:
        """Get the total number of transcript entries."""
        return len(self.entries)

    @property
    def tool_call_count(self) -> int:
        """Get the total number of tool calls."""
        return sum(len(e.tool_calls) for e in self.entries)

    @property
    def php_files(self) -> list[FileChange]:
        """Get only PHP file changes."""
        return [f for f in self.file_changes if f.is_php]

    @property
    def frontend_files(self) -> list[FileChange]:
        """Get only frontend file changes (Vue, TS, JS)."""
        return [f for f in self.file_changes if f.is_frontend]

    @property
    def has_php_changes(self) -> bool:
        """Check if any PHP files were modified."""
        return len(self.php_files) > 0

    @property
    def has_frontend_changes(self) -> bool:
        """Check if any frontend files were modified."""
        return len(self.frontend_files) > 0

    def get_files_matching(self, patterns: list[str]) -> list[FileChange]:
        """
        Get files matching any of the given patterns.

        Args:
            patterns: List of patterns like ["*.php", "*.vue"]

        Returns:
            List of matching file changes
        """
        return [f for f in self.file_changes if f.matches_any_pattern(patterns)]

    @property
    def unique_file_paths(self) -> list[str]:
        """Get unique file paths (deduplicated)."""
        seen = set()
        result = []
        for fc in self.file_changes:
            if fc.path not in seen:
                seen.add(fc.path)
                result.append(fc.path)
        return result

    def format_files_for_display(self) -> str:
        """
        Format file changes for display/logging.

        Returns:
            Multi-line string listing files and their actions
        """
        if not self.file_changes:
            return "(no files changed)"

        lines = []
        for fc in self.file_changes:
            lines.append(f"  - {fc.path} ({fc.action.value})")
        return "\n".join(lines)

    def format_files_for_review(self) -> str:
        """
        Format file paths for passing to the review tool.

        Returns:
            Comma-separated list of file paths
        """
        return ", ".join(self.unique_file_paths)

    def __str__(self) -> str:
        return (
            f"TranscriptAnalysis(agent={self.agent_id}, "
            f"files={self.file_change_count}, "
            f"entries={self.entry_count})"
        )
