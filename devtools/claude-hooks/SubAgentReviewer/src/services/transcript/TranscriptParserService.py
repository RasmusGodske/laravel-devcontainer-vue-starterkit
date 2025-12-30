"""
Service for parsing Claude Code agent transcripts.
"""

import json
from pathlib import Path

from ...models.transcript import FileChange, FileChangeAction, TranscriptEntry
from ...models.TranscriptAnalysis import TranscriptAnalysis


class TranscriptParserService:
    """
    Parses Claude Code agent transcript JSONL files.

    Extracts:
    - Initial prompt (the task given to the agent)
    - File changes (files created/edited via tool calls)
    - Metadata (agent ID, session ID)

    Example:
        parser = TranscriptParserService()
        analysis = parser.parse(Path("~/.claude/projects/.../agent-abc123.jsonl"))
        print(analysis.initial_prompt)
        for file in analysis.file_changes:
            print(f"  {file.path} ({file.action.value})")
    """

    def parse(self, transcript_path: Path) -> TranscriptAnalysis:
        """
        Parse a transcript file and extract relevant information.

        Args:
            transcript_path: Path to the agent transcript JSONL file

        Returns:
            TranscriptAnalysis with extracted data

        Raises:
            FileNotFoundError: If the transcript file doesn't exist
            json.JSONDecodeError: If a line contains invalid JSON
        """
        if not transcript_path.exists():
            raise FileNotFoundError(f"Transcript not found: {transcript_path}")

        entries = self._read_entries(transcript_path)

        # Extract metadata from first entry
        agent_id = ""
        session_id = ""
        if entries:
            agent_id = entries[0].agent_id
            session_id = entries[0].session_id

        # Find initial prompt
        initial_prompt = self._extract_initial_prompt(entries)

        # Extract file changes
        file_changes = self._extract_file_changes(entries)

        return TranscriptAnalysis(
            agent_id=agent_id,
            session_id=session_id,
            transcript_path=transcript_path,
            initial_prompt=initial_prompt,
            file_changes=file_changes,
            entries=entries,
        )

    def _read_entries(self, transcript_path: Path) -> list[TranscriptEntry]:
        """
        Read all entries from the transcript file.

        Args:
            transcript_path: Path to the JSONL file

        Returns:
            List of parsed TranscriptEntry objects
        """
        entries = []

        with open(transcript_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    entry = TranscriptEntry.from_dict(data)
                    entries.append(entry)
                except json.JSONDecodeError as e:
                    # Log but continue - don't fail on one bad line
                    # In production, we might want to log this
                    continue

        return entries

    def _extract_initial_prompt(self, entries: list[TranscriptEntry]) -> str:
        """
        Extract the initial prompt from the transcript entries.

        The initial prompt is the first user message with no parent.

        Args:
            entries: List of transcript entries

        Returns:
            The initial prompt text, or empty string if not found
        """
        for entry in entries:
            if entry.is_initial_prompt:
                return entry.initial_prompt_text or ""

        return ""

    def _extract_file_changes(
        self, entries: list[TranscriptEntry]
    ) -> list[FileChange]:
        """
        Extract file changes from tool calls in the transcript.

        Looks for file-modifying tool calls like Edit, Write,
        and Serena symbol operations.

        Args:
            entries: List of transcript entries

        Returns:
            List of FileChange objects (deduplicated by path)
        """
        seen_paths: set[str] = set()
        file_changes: list[FileChange] = []

        for entry in entries:
            for tool_call in entry.file_modifying_tool_calls:
                path = tool_call.file_path
                if not path:
                    continue

                # Skip if we've already seen this path
                if path in seen_paths:
                    continue
                seen_paths.add(path)

                # Determine action based on tool name
                action = self._determine_action(tool_call.name)

                file_changes.append(
                    FileChange(
                        path=path,
                        action=action,
                        tool_name=tool_call.name,
                        tool_call_id=tool_call.id,
                        tool_input=tool_call.input,
                    )
                )

        return file_changes

    def _determine_action(self, tool_name: str) -> FileChangeAction:
        """
        Determine the file change action based on the tool name.

        Args:
            tool_name: Name of the tool that modified the file

        Returns:
            FileChangeAction (CREATED, EDITED, or UNKNOWN)
        """
        if tool_name == "Write":
            return FileChangeAction.CREATED
        elif tool_name in ("Edit", "MultiEdit"):
            return FileChangeAction.EDITED
        elif tool_name.startswith("mcp__serena__"):
            # Serena tools are typically edits to existing code
            return FileChangeAction.EDITED
        else:
            return FileChangeAction.UNKNOWN
