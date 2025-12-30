"""Sync service for telemetry data."""

import shutil
import socket
from datetime import datetime, timezone
from pathlib import Path

from ..models import SyncConfig, SyncResult, SyncStatus
from .git_service import GitService


class SyncService:
    """Service for syncing telemetry data to shared branch."""

    def __init__(self, config: SyncConfig, git: GitService) -> None:
        """
        Initialize sync service.

        Args:
            config: Sync configuration
            git: Git service instance
        """
        self.config = config
        self.git = git

    def status(self) -> SyncStatus:
        """
        Get current sync status.

        Returns:
            SyncStatus with setup state and pending files
        """
        branch_exists = self.git.branch_exists(self.config.branch_name)
        worktree_exists = self.git.worktree_exists(self.config.worktree_path)

        pending_files: list[str] = []
        if self.config.source_dir.exists():
            pending_files = self._get_syncable_files()

        return SyncStatus(
            worktree_exists=worktree_exists,
            branch_exists=branch_exists,
            pending_files=pending_files,
            pending_count=len(pending_files),
        )

    def setup(self) -> SyncResult:
        """
        Set up telemetry sync (create branch and worktree).

        Returns:
            SyncResult indicating success/failure
        """
        try:
            # Check if already set up
            status = self.status()
            if status.is_setup:
                return SyncResult(
                    success=True,
                    message="Already set up",
                )

            # Create branch if needed
            if not status.branch_exists:
                self.git.create_orphan_branch(self.config.branch_name)

            # Create worktree if needed
            if not status.worktree_exists:
                self.git.create_worktree(
                    self.config.worktree_path,
                    self.config.branch_name,
                )

            return SyncResult(
                success=True,
                message=f"Setup complete. Worktree at: {self.config.worktree_path}",
            )

        except Exception as e:
            return SyncResult(
                success=False,
                message=f"Setup failed: {e}",
            )

    def sync(self, message: str | None = None) -> SyncResult:
        """
        Sync local telemetry to shared branch.

        Args:
            message: Optional custom commit message

        Returns:
            SyncResult indicating success/failure
        """
        try:
            # Check setup
            status = self.status()
            if not status.is_setup:
                return SyncResult(
                    success=False,
                    message="Not set up. Run 'setup' first.",
                )

            # Check for files to sync
            if status.pending_count == 0:
                return SyncResult(
                    success=True,
                    message="No files to sync",
                    files_synced=0,
                )

            # Copy files to worktree
            files_copied = self._copy_files_to_worktree()

            # Stage changes
            self.git.add_all(self.config.worktree_path)

            # Generate commit message
            if message is None:
                hostname = socket.gethostname()
                timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                message = f"Sync telemetry from {hostname} at {timestamp}"

            # Commit
            commit_hash = self.git.commit(self.config.worktree_path, message)

            if commit_hash is None:
                return SyncResult(
                    success=True,
                    message="No changes to commit",
                    files_synced=0,
                )

            # Push
            if not self.git.push(self.config.worktree_path):
                return SyncResult(
                    success=False,
                    message="Push failed. Changes committed locally.",
                    files_synced=files_copied,
                    commit_hash=commit_hash,
                )

            return SyncResult(
                success=True,
                message=f"Synced {files_copied} files",
                files_synced=files_copied,
                commit_hash=commit_hash,
            )

        except Exception as e:
            return SyncResult(
                success=False,
                message=f"Sync failed: {e}",
            )

    def _get_syncable_files(self) -> list[str]:
        """Get list of files that would be synced (excluding .gitignore, etc.)."""
        if not self.config.source_dir.exists():
            return []

        files: list[str] = []
        exclude = {".gitignore", ".gitkeep", "README.md"}

        for path in self.config.source_dir.rglob("*"):
            if path.is_file() and path.name not in exclude:
                rel_path = path.relative_to(self.config.source_dir)
                files.append(str(rel_path))

        return sorted(files)

    def _copy_files_to_worktree(self) -> int:
        """
        Copy files from source to worktree.

        Returns:
            Number of files copied
        """
        if not self.config.source_dir.exists():
            return 0

        files_copied = 0
        exclude = {".gitignore", ".gitkeep"}  # Keep README.md for the branch

        for source_path in self.config.source_dir.rglob("*"):
            if source_path.is_file() and source_path.name not in exclude:
                rel_path = source_path.relative_to(self.config.source_dir)
                dest_path = self.config.worktree_path / rel_path

                # Create parent directories
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy file
                shutil.copy2(source_path, dest_path)
                files_copied += 1

        return files_copied
