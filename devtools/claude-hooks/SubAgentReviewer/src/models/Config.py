"""
Data classes for the SubAgentReviewer configuration.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ReviewerSettings:
    """Global settings for the reviewer."""

    skip_if_no_file_changes: bool = True
    max_review_cycles: int = 3

    @classmethod
    def from_dict(cls, data: dict) -> "ReviewerSettings":
        """Parse from a dictionary."""
        return cls(
            skip_if_no_file_changes=data.get("skip_if_no_file_changes", True),
            max_review_cycles=data.get("max_review_cycles", 3),
        )


@dataclass
class ReviewerConfig:
    """
    Configuration for the SubAgentReviewer.

    Loaded from config.json in the SubAgentReviewer2 directory.

    Example config.json:
    ```json
    {
      "output_dir": "analytics/subagent-reviewer",
      "agents_to_review": [
        "backend-engineer",
        "frontend-engineer"
      ],
      "settings": {
        "skip_if_no_file_changes": true,
        "max_review_cycles": 3
      }
    }
    ```

    The output_dir can be:
    - Relative path: Resolved from project root (e.g., "analytics/subagent-reviewer")
    - Absolute path: Used as-is
    - Not specified: Defaults to tool's own directory (sessions/)
    """

    agents_to_review: list[str] = field(default_factory=list)
    settings: ReviewerSettings = field(default_factory=ReviewerSettings)
    output_dir: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "ReviewerConfig":
        """Parse from a dictionary."""
        agents = data.get("agents_to_review", [])
        settings = ReviewerSettings.from_dict(data.get("settings", {}))
        output_dir = data.get("output_dir")
        return cls(
            agents_to_review=agents,
            settings=settings,
            output_dir=output_dir,
        )

    @classmethod
    def load(cls, config_path: Path) -> "ReviewerConfig":
        """
        Load configuration from a JSON file.

        Args:
            config_path: Path to the config.json file

        Returns:
            Parsed ReviewerConfig

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls.from_dict(data)

    def should_review_agent(self, agent_type: str) -> bool:
        """
        Check if an agent type should be reviewed.

        Args:
            agent_type: The agent type (e.g., "backend-engineer")

        Returns:
            True if this agent type should be reviewed
        """
        return agent_type in self.agents_to_review
