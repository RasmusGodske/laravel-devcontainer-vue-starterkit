"""Configuration loading for telemetry sync."""

import json
from pathlib import Path

from .models import SyncConfig

# Defaults
DEFAULT_BRANCH_NAME = "devtools-telemetry"
DEFAULT_SOURCE_DIR = "devtools-telemetry"
DEFAULT_WORKTREE_DIR = "project-telemetry"


def load_config(config_path: Path, project_root: Path) -> SyncConfig:
    """
    Load sync configuration from JSON file.

    Args:
        config_path: Path to config.json
        project_root: Project root directory

    Returns:
        SyncConfig with resolved paths
    """
    config_data: dict = {}

    if config_path.exists():
        try:
            with open(config_path) as f:
                config_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass  # Use defaults

    branch_name = config_data.get("branch_name", DEFAULT_BRANCH_NAME)
    source_dir_str = config_data.get("source_dir", DEFAULT_SOURCE_DIR)
    worktree_dir_str = config_data.get("worktree_dir", DEFAULT_WORKTREE_DIR)

    # Resolve source_dir (relative to project root)
    source_path = Path(source_dir_str)
    if not source_path.is_absolute():
        source_path = project_root / source_path

    # Resolve worktree_path (sibling to project root)
    worktree_path = Path(worktree_dir_str)
    if not worktree_path.is_absolute():
        worktree_path = project_root.parent / worktree_dir_str

    return SyncConfig(
        branch_name=branch_name,
        worktree_path=worktree_path,
        source_dir=source_path,
        project_root=project_root,
    )
