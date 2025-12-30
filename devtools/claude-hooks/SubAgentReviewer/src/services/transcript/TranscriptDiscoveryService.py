"""
Service for discovering agent transcript files.
"""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DiscoveredAgent:
    """
    Information about a discovered agent from the main session transcript.

    Contains the agent ID and metadata extracted from the toolUseResult.
    """

    agent_id: str
    transcript_path: Path
    status: str
    prompt: str
    total_duration_ms: int
    total_tool_use_count: int

    @property
    def exists(self) -> bool:
        """Check if the agent transcript file exists."""
        return self.transcript_path.exists()

    def __str__(self) -> str:
        return f"DiscoveredAgent(id={self.agent_id}, status={self.status})"


class TranscriptDiscoveryService:
    """
    Discovers agent transcripts by parsing the main session transcript.

    Instead of searching for files by modification time (which has race conditions),
    this service:
    1. Parses the main session transcript (provided by the hook)
    2. Finds toolUseResult entries with agentId
    3. Maps agent IDs to their transcript files: agent-{agentId}.jsonl

    This is deterministic and avoids race conditions because we follow the direct
    link from main session → agent.

    Example:
        discovery = TranscriptDiscoveryService()
        agents = discovery.find_agents_from_main_transcript(
            main_transcript_path=Path("~/.claude/projects/.../session.jsonl")
        )
        for agent in agents:
            print(f"Agent {agent.agent_id}: {agent.transcript_path}")
    """

    def find_agents_from_main_transcript(
        self,
        main_transcript_path: Path,
    ) -> list[DiscoveredAgent]:
        """
        Find all agents referenced in the main session transcript.

        Parses the main transcript and extracts agent information from
        toolUseResult entries that contain agentId.

        Args:
            main_transcript_path: Path to the main session transcript

        Returns:
            List of DiscoveredAgent, ordered by appearance in transcript
        """
        if not main_transcript_path.exists():
            return []

        transcript_dir = main_transcript_path.parent
        agents: list[DiscoveredAgent] = []
        seen_agent_ids: set[str] = set()

        with open(main_transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Look for toolUseResult with agentId
                tool_use_result = data.get("toolUseResult")
                if not tool_use_result:
                    continue

                agent_id = tool_use_result.get("agentId")
                if not agent_id:
                    continue

                # Skip duplicates (same agent might appear multiple times
                # if the transcript is being read while agent is active)
                if agent_id in seen_agent_ids:
                    continue
                seen_agent_ids.add(agent_id)

                agent_transcript_path = transcript_dir / f"agent-{agent_id}.jsonl"

                agents.append(
                    DiscoveredAgent(
                        agent_id=agent_id,
                        transcript_path=agent_transcript_path,
                        status=tool_use_result.get("status", "unknown"),
                        prompt=tool_use_result.get("prompt", ""),
                        total_duration_ms=tool_use_result.get("totalDurationMs", 0),
                        total_tool_use_count=tool_use_result.get("totalToolUseCount", 0),
                    )
                )

        return agents

    def find_most_recent_agent(
        self,
        main_transcript_path: Path,
    ) -> DiscoveredAgent | None:
        """
        Find the most recently completed agent from the main transcript.

        The most recent agent is the last one that appears in the transcript
        (since entries are appended chronologically).

        Args:
            main_transcript_path: Path to the main session transcript

        Returns:
            The most recent DiscoveredAgent, or None if no agents found
        """
        agents = self.find_agents_from_main_transcript(main_transcript_path)
        if not agents:
            return None

        # Return the last one (most recent)
        return agents[-1]

    def find_agent_by_id(
        self,
        main_transcript_path: Path,
        agent_id: str,
    ) -> DiscoveredAgent | None:
        """
        Find a specific agent by ID from the main transcript.

        Args:
            main_transcript_path: Path to the main session transcript
            agent_id: The agent ID to find

        Returns:
            The DiscoveredAgent if found, None otherwise
        """
        agents = self.find_agents_from_main_transcript(main_transcript_path)
        for agent in agents:
            if agent.agent_id == agent_id:
                return agent
        return None

    @staticmethod
    def get_agent_transcript_path(transcript_dir: Path, agent_id: str) -> Path:
        """
        Get the expected path for an agent's transcript.

        Args:
            transcript_dir: Directory containing transcript files
            agent_id: The agent ID

        Returns:
            Path to the agent transcript (may not exist)
        """
        return transcript_dir / f"agent-{agent_id}.jsonl"
