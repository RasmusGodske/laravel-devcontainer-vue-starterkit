"""Git operations for telemetry sync."""

import subprocess
from pathlib import Path


class GitService:
    """Service for git operations."""

    def __init__(self, project_root: Path) -> None:
        """
        Initialize git service.

        Args:
            project_root: Project root directory (git repo)
        """
        self.project_root = project_root

    def _run(
        self,
        args: list[str],
        cwd: Path | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        """Run a git command."""
        return subprocess.run(
            ["git", *args],
            cwd=cwd or self.project_root,
            capture_output=True,
            text=True,
            check=check,
        )

    def branch_exists(self, branch: str) -> bool:
        """Check if a branch exists (local or remote)."""
        # Check local
        result = self._run(
            ["show-ref", "--verify", f"refs/heads/{branch}"],
            check=False,
        )
        if result.returncode == 0:
            return True

        # Check remote
        result = self._run(
            ["ls-remote", "--heads", "origin", branch],
            check=False,
        )
        return bool(result.stdout.strip())

    def create_orphan_branch(self, branch: str) -> None:
        """
        Create an orphan branch with no history.

        Uses git plumbing commands to avoid affecting the working directory.
        This is safe to run even with uncommitted changes.

        Args:
            branch: Branch name to create
        """
        # Create an empty tree object
        result = self._run(["hash-object", "-t", "tree", "/dev/null"])
        empty_tree = result.stdout.strip()

        # Create a commit pointing to the empty tree (no parent = orphan)
        result = self._run([
            "commit-tree",
            empty_tree,
            "-m",
            "Initial telemetry branch",
        ])
        commit_hash = result.stdout.strip()

        # Create the branch pointing to that commit
        self._run(["branch", branch, commit_hash])

        # Push to remote
        self._run(["push", "-u", "origin", branch])

    def worktree_exists(self, path: Path) -> bool:
        """Check if a worktree exists at the given path."""
        return path.exists() and (path / ".git").exists()

    def create_worktree(self, path: Path, branch: str) -> None:
        """
        Create a worktree for the given branch.

        Args:
            path: Path for the worktree
            branch: Branch to checkout in worktree
        """
        self._run(["worktree", "add", str(path), branch])

    def add_all(self, worktree: Path) -> None:
        """Stage all changes in the worktree."""
        self._run(["add", "-A"], cwd=worktree)

    def has_changes(self, worktree: Path) -> bool:
        """Check if there are staged changes."""
        result = self._run(["diff", "--cached", "--quiet"], cwd=worktree, check=False)
        return result.returncode != 0

    def commit(self, worktree: Path, message: str) -> str | None:
        """
        Commit staged changes.

        Args:
            worktree: Worktree path
            message: Commit message

        Returns:
            Commit hash if successful, None if nothing to commit
        """
        if not self.has_changes(worktree):
            return None

        self._run(["commit", "-m", message], cwd=worktree)

        # Get commit hash
        result = self._run(["rev-parse", "HEAD"], cwd=worktree)
        return result.stdout.strip()

    def push(self, worktree: Path) -> bool:
        """
        Push changes from worktree.

        Args:
            worktree: Worktree path

        Returns:
            True if push succeeded
        """
        result = self._run(["push"], cwd=worktree, check=False)
        return result.returncode == 0

    def pull(self, worktree: Path) -> bool:
        """
        Pull latest changes to worktree.

        Args:
            worktree: Worktree path

        Returns:
            True if pull succeeded
        """
        result = self._run(["pull"], cwd=worktree, check=False)
        return result.returncode == 0
