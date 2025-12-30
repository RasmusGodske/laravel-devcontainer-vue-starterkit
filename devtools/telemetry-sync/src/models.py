"""Data models for telemetry sync."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SyncConfig:
    """Configuration for telemetry sync."""

    branch_name: str
    worktree_path: Path
    source_dir: Path
    project_root: Path

    def __post_init__(self) -> None:
        """Ensure paths are Path objects."""
        if isinstance(self.worktree_path, str):
            self.worktree_path = Path(self.worktree_path)
        if isinstance(self.source_dir, str):
            self.source_dir = Path(self.source_dir)
        if isinstance(self.project_root, str):
            self.project_root = Path(self.project_root)


@dataclass
class SyncResult:
    """Result of a sync operation."""

    success: bool
    message: str
    files_synced: int = 0
    commit_hash: str | None = None


@dataclass
class SyncStatus:
    """Status of telemetry sync setup and pending files."""

    worktree_exists: bool
    branch_exists: bool
    pending_files: list[str] = field(default_factory=list)
    pending_count: int = 0

    @property
    def is_setup(self) -> bool:
        """Check if sync is properly set up."""
        return self.worktree_exists and self.branch_exists
