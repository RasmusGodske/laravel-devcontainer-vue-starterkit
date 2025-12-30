"""
Data classes for session tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AgentReview:
    """
    Represents a single review of an agent's work.

    Lifecycle:
    1. Created when review starts (decision=None, ended_at=None)
    2. Updated when review ends (decision=True/False, ended_at=timestamp, usage stats)

    Example:
    ```json
    {
      "started_at": "2025-12-11T09:09:36.123456",
      "ended_at": "2025-12-11T09:10:16.123456",
      "decision": false,
      "input_tokens": 12500,
      "output_tokens": 800,
      "total_cost_usd": 0.042
    }
    ```
    """

    started_at: str
    ended_at: str | None = None
    decision: bool | None = None  # True=passed, False=blocked, None=in_progress
    input_tokens: int = 0
    output_tokens: int = 0
    total_cost_usd: float | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentReview":
        """Parse from a dictionary."""
        return cls(
            started_at=data.get("started_at", ""),
            ended_at=data.get("ended_at"),
            decision=data.get("decision"),
            input_tokens=data.get("input_tokens", 0),
            output_tokens=data.get("output_tokens", 0),
            total_cost_usd=data.get("total_cost_usd"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary for JSON serialization."""
        return {
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "decision": self.decision,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_cost_usd": self.total_cost_usd,
        }

    @property
    def is_completed(self) -> bool:
        """Check if the review has completed."""
        return self.ended_at is not None

    @property
    def is_in_progress(self) -> bool:
        """Check if the review is still in progress."""
        return self.ended_at is None

    @property
    def passed(self) -> bool:
        """Check if the review passed."""
        return self.decision is True

    @property
    def blocked(self) -> bool:
        """Check if the review was blocked."""
        return self.decision is False


@dataclass
class TrackedAgent:
    """
    An agent tracked within a session.

    Created when SubagentStart fires, updated when SubagentStop fires.
    Reviews are tracked as a list of AgentReview objects.

    Example:
    ```json
    {
      "agent_id": "ad3ac8a",
      "agent_type": "backend-engineer",
      "started_at": "2025-12-11T09:05:14.123456",
      "ended_at": "2025-12-11T09:11:17.123456",
      "transcript_path": "/home/vscode/.claude/...",
      "reviews": [
        {
          "started_at": "2025-12-11T09:09:36.123456",
          "ended_at": "2025-12-11T09:10:16.123456",
          "decision": false
        },
        {
          "started_at": "2025-12-11T09:10:56.123456",
          "ended_at": "2025-12-11T09:11:17.123456",
          "decision": true
        }
      ]
    }
    ```
    """

    agent_id: str
    agent_type: str
    started_at: str
    ended_at: str | None = None
    transcript_path: str | None = None
    reviews: list[AgentReview] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrackedAgent":
        """Parse from a dictionary."""
        reviews_data = data.get("reviews", [])
        reviews = [AgentReview.from_dict(r) for r in reviews_data]

        return cls(
            agent_id=data.get("agent_id", ""),
            agent_type=data.get("agent_type", ""),
            started_at=data.get("started_at", ""),
            ended_at=data.get("ended_at"),
            transcript_path=data.get("transcript_path"),
            reviews=reviews,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary for JSON serialization."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "transcript_path": self.transcript_path,
            "reviews": [r.to_dict() for r in self.reviews],
        }

    @property
    def has_ended(self) -> bool:
        """Check if the agent has ended."""
        return self.ended_at is not None

    @property
    def review_count(self) -> int:
        """Get the number of reviews performed."""
        return len(self.reviews)

    @property
    def completed_review_count(self) -> int:
        """Get the number of completed reviews."""
        return sum(1 for r in self.reviews if r.is_completed)

    @property
    def has_been_reviewed(self) -> bool:
        """Check if the agent has had at least one completed review."""
        return any(r.is_completed for r in self.reviews)

    @property
    def latest_review(self) -> AgentReview | None:
        """Get the most recent review."""
        return self.reviews[-1] if self.reviews else None

    @property
    def latest_decision(self) -> bool | None:
        """Get the most recent completed review decision."""
        for review in reversed(self.reviews):
            if review.is_completed:
                return review.decision
        return None

    def start_review(self) -> AgentReview:
        """
        Start a new review.

        Returns:
            The created AgentReview
        """
        review = AgentReview(started_at=datetime.now().isoformat())
        self.reviews.append(review)
        return review

    def end_review(
        self,
        passed: bool,
        input_tokens: int = 0,
        output_tokens: int = 0,
        total_cost_usd: float | None = None,
    ) -> AgentReview | None:
        """
        End the current (latest) review with a decision and usage stats.

        Args:
            passed: True if review passed, False if blocked
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            total_cost_usd: Total cost in USD

        Returns:
            The updated AgentReview, or None if no reviews exist
        """
        if not self.reviews:
            return None

        review = self.reviews[-1]
        review.ended_at = datetime.now().isoformat()
        review.decision = passed
        review.input_tokens = input_tokens
        review.output_tokens = output_tokens
        review.total_cost_usd = total_cost_usd
        return review


@dataclass
class Session:
    """
    Represents a Claude Code session with tracked agents.

    Stored as session.json in the session directory.

    Example:
    ```json
    {
      "session_id": "4704b6bb-9905-4c26-8fee-f3f692325a29",
      "started_at": "2025-12-10T16:53:12.101452",
      "git_branch": "feature/my-feature",
      "git_commit": "3c322d03",
      "transcript_path": "/home/vscode/.claude/projects/.../session.jsonl",
      "agents": {
        "64fc4031": {
          "agent_id": "64fc4031",
          "agent_type": "Explore",
          "started_at": "2025-12-10T16:53:12.101452",
          "ended_at": "2025-12-10T16:54:17.334317",
          "transcript_path": "/home/vscode/.claude/projects/.../agent-64fc4031.jsonl",
          "reviews": []
        }
      }
    }
    ```
    """

    session_id: str
    started_at: str
    transcript_path: str = ""
    git_branch: str | None = None
    git_commit: str | None = None
    agents: dict[str, TrackedAgent] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Session":
        """Parse from a dictionary."""
        agents_data = data.get("agents", {})
        agents = {
            agent_id: TrackedAgent.from_dict(agent_data)
            for agent_id, agent_data in agents_data.items()
        }
        return cls(
            session_id=data.get("session_id", ""),
            started_at=data.get("started_at", ""),
            transcript_path=data.get("transcript_path", ""),
            git_branch=data.get("git_branch"),
            git_commit=data.get("git_commit"),
            agents=agents,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "git_branch": self.git_branch,
            "git_commit": self.git_commit,
            "transcript_path": self.transcript_path,
            "agents": {
                agent_id: agent.to_dict()
                for agent_id, agent in self.agents.items()
            },
        }

    def add_agent(
        self,
        agent_id: str,
        agent_type: str,
        started_at: str | None = None,
    ) -> TrackedAgent:
        """
        Add a new agent to the session (called on SubagentStart).

        If agent already exists (e.g., due to retry), returns existing
        agent to preserve reviews and other data.

        Args:
            agent_id: The agent's unique ID
            agent_type: The agent type (e.g., "backend-engineer")
            started_at: Timestamp when agent started (defaults to now)

        Returns:
            The created or existing TrackedAgent
        """
        # Return existing agent to preserve reviews
        if agent_id in self.agents:
            return self.agents[agent_id]

        if started_at is None:
            started_at = datetime.now().isoformat()

        agent = TrackedAgent(
            agent_id=agent_id,
            agent_type=agent_type,
            started_at=started_at,
        )
        self.agents[agent_id] = agent
        return agent

    def end_agent(
        self,
        agent_id: str,
        transcript_path: str | None = None,
        ended_at: str | None = None,
    ) -> TrackedAgent | None:
        """
        Mark an agent as ended (called on SubagentStop).

        Args:
            agent_id: The agent's unique ID
            transcript_path: Path to the agent's transcript
            ended_at: Timestamp when agent ended (defaults to now)

        Returns:
            The updated TrackedAgent, or None if not found
        """
        agent = self.agents.get(agent_id)
        if agent is None:
            return None

        if ended_at is None:
            ended_at = datetime.now().isoformat()

        agent.ended_at = ended_at
        agent.transcript_path = transcript_path
        return agent

    def get_agent(self, agent_id: str) -> TrackedAgent | None:
        """Get an agent by ID."""
        return self.agents.get(agent_id)

    def get_agent_type(self, agent_id: str) -> str | None:
        """
        Get the agent type for an agent ID.

        This is the key method for SubagentStop to look up agent_type.

        Args:
            agent_id: The agent's unique ID

        Returns:
            The agent type, or None if not found
        """
        agent = self.agents.get(agent_id)
        return agent.agent_type if agent else None

    def start_agent_review(self, agent_id: str) -> AgentReview | None:
        """
        Start a new review for an agent.

        Args:
            agent_id: The agent's unique ID

        Returns:
            The created AgentReview, or None if agent not found
        """
        agent = self.agents.get(agent_id)
        if agent is None:
            return None
        return agent.start_review()

    def end_agent_review(
        self,
        agent_id: str,
        passed: bool,
        input_tokens: int = 0,
        output_tokens: int = 0,
        total_cost_usd: float | None = None,
    ) -> AgentReview | None:
        """
        End the current review for an agent.

        Args:
            agent_id: The agent's unique ID
            passed: True if review passed, False if blocked
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            total_cost_usd: Total cost in USD

        Returns:
            The updated AgentReview, or None if agent not found
        """
        agent = self.agents.get(agent_id)
        if agent is None:
            return None
        return agent.end_review(
            passed=passed,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_cost_usd=total_cost_usd,
        )

    def get_agent_review_count(self, agent_id: str) -> int:
        """
        Get the number of completed reviews for an agent.

        Args:
            agent_id: The agent's unique ID

        Returns:
            The number of completed reviews, or 0 if agent not found
        """
        agent = self.agents.get(agent_id)
        return agent.completed_review_count if agent else 0
