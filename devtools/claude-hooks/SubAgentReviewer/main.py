#!/usr/bin/env python3
"""
SubAgentReviewer2 - Hook handler for reviewing subagent code changes.

Handles two Claude Code hooks:
- SubagentStart: Track agent type for later lookup
- SubagentStop: Review code changes if agent type requires it

Usage (called automatically by Claude Code):
    echo '{"session_id": "...", ...}' | python main.py

Output:
- Exit 0 with no JSON: Allow subagent to proceed
- Exit 0 with {"decision": "block", "reason": "..."}: Block and send feedback
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src import (
    Paths,
    GlobalLogger,
    AgentLogger,
    ReviewLogger,
    HookInput,
    ReviewerConfig,
    ReviewDetails,
    ReviewFileChange,
    ReviewerService,
    ReviewMarkdownFormatter,
    ReviewContext,
    SessionStorageService,
    TranscriptParserService,
)


def get_git_info(cwd: Path | None = None) -> tuple[str | None, str | None]:
    """
    Get current git branch and commit hash.

    Args:
        cwd: Working directory for git commands

    Returns:
        Tuple of (branch, commit_hash) or (None, None) on error
    """
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd,
        ).stdout.strip()

        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd,
        ).stdout.strip()

        return branch, commit
    except Exception:
        return None, None


class HookResult:
    """Result of processing a hook."""

    def __init__(self, decision: str, reason: str, should_block: bool = False):
        self.decision = decision
        self.reason = reason
        self.should_block = should_block


class SubagentReviewerHook:
    """
    Main hook handler for reviewing subagent code changes.

    Handles two events:
    - SubagentStart: Store agent_id → agent_type mapping
    - SubagentStop: Look up agent_type, review if needed
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize the hook handler.

        Args:
            verbose: If True, enable debug logging to stderr
        """
        self._verbose = verbose

        # Load config first to get output_dir
        self._config = self._load_config_early()

        # Create Paths with output_dir from config
        self._paths = Paths(output_dir=self._config.output_dir)

        self._global_logger = GlobalLogger(
            paths=self._paths,
            verbose=verbose,
            also_stderr=verbose,
        )
        self._session_storage = SessionStorageService(
            sessions_dir=self._paths.sessions_dir,
        )
        self._parser_service = TranscriptParserService()
        self._reviewer_service = ReviewerService(
            tool_path=self._paths.devtools_dir / "code-reviewer" / "cli.py",
            timeout_seconds=90,
            project_dir=self._paths.project_root,
        )

    @staticmethod
    def _load_config_early() -> ReviewerConfig:
        """Load configuration early (before Paths is fully initialized)."""
        # Get base dir directly (same logic as Paths._get_default_base_dir)
        base_dir = Path(__file__).parent
        config_path = base_dir / "config.json"

        if not config_path.exists():
            # Return default config if no config file
            return ReviewerConfig()

        return ReviewerConfig.load(config_path)

    def _load_config(self) -> ReviewerConfig:
        """Get the loaded configuration."""
        return self._config

    def run(self, raw_input: dict) -> int:
        """
        Run the hook with the given input data.

        Args:
            raw_input: The JSON input from Claude Code

        Returns:
            Exit code (0 for success)
        """
        start_time = time.time()

        # Parse input
        hook_input = HookInput.from_dict(raw_input)

        # Log hook start
        self._global_logger.log_hook_start(
            hook_input.session_id,
            hook_input.hook_event_name,
        )
        self._global_logger.debug(f"Raw input: {json.dumps(raw_input, indent=2)}")

        try:
            if hook_input.is_start_event:
                result = self._handle_start(hook_input)
            elif hook_input.is_stop_event:
                result = self._handle_stop(hook_input)
            else:
                result = self._allow(f"Unknown event: {hook_input.hook_event_name}")
        except Exception as e:
            self._global_logger.exception(f"Error processing hook: {e}")
            result = self._allow("Error during processing")

        # Log completion
        duration_ms = int((time.time() - start_time) * 1000)
        self._global_logger.log_hook_end(
            hook_input.session_id,
            result.decision,
            duration_ms,
        )
        self._global_logger.close()

        # Output block decision if needed
        if result.should_block:
            print(json.dumps({
                "decision": "block",
                "reason": result.reason,
            }))

        return 0

    def _handle_start(self, hook_input: HookInput) -> HookResult:
        """
        Handle SubagentStart event.

        Store the agent_id → agent_type mapping for later lookup.
        Only creates agent directory if agent type will be reviewed.
        """
        if not hook_input.has_agent_id:
            self._global_logger.warning("SubagentStart without agent_id")
            return self._allow("No agent_id in SubagentStart")

        if not hook_input.has_agent_type:
            self._global_logger.warning("SubagentStart without agent_type")
            return self._allow("No agent_type in SubagentStart")

        # Get git info for session tracking
        git_branch, git_commit = get_git_info(self._paths.project_root)

        # Check if this agent type will be reviewed (only create directory if so)
        config = self._load_config()
        will_be_reviewed = config.should_review_agent(hook_input.agent_type)

        # Track the agent start (only create directory for agents that will be reviewed)
        session, agent_dir = self._session_storage.track_agent_start(
            session_id=hook_input.session_id,
            agent_id=hook_input.agent_id,
            agent_type=hook_input.agent_type,
            transcript_path=str(hook_input.transcript_path) if hook_input.transcript_path else "",
            git_branch=git_branch,
            git_commit=git_commit,
            create_directory=will_be_reviewed,
        )

        self._global_logger.info(
            f"Tracked agent start: {hook_input.agent_id} ({hook_input.agent_type})"
        )
        if agent_dir:
            self._global_logger.debug(f"Agent dir: {agent_dir}")

        return self._allow("Agent start tracked")

    def _handle_stop(self, hook_input: HookInput) -> HookResult:
        """
        Handle SubagentStop event.

        Look up agent_type and review if needed.
        On retries (stop_hook_active=True), re-review to verify fixes.
        """
        if not hook_input.has_agent_id:
            self._global_logger.warning("SubagentStop without agent_id")
            return self._allow("No agent_id in SubagentStop")

        # Track the agent stop and get the agent info
        session, agent, agent_dir = self._session_storage.track_agent_stop(
            session_id=hook_input.session_id,
            agent_id=hook_input.agent_id,
            agent_transcript_path=str(hook_input.agent_transcript_path) if hook_input.agent_transcript_path else None,
        )

        if agent is None:
            self._global_logger.warning(
                f"Agent {hook_input.agent_id} not found in session storage"
            )
            return self._allow("Agent not tracked (probably started before hook was installed)")

        if agent_dir is not None:
            self._global_logger.debug(f"Agent dir: {agent_dir}")

        agent_type = agent.agent_type
        self._global_logger.info(f"Agent stopped: {hook_input.agent_id} ({agent_type})")

        # Load config and check if we should review this agent type
        try:
            config = self._load_config()
        except FileNotFoundError as e:
            self._global_logger.error(f"Config not found: {e}")
            return self._allow("Config file not found")

        if not config.should_review_agent(agent_type):
            self._global_logger.info(f"Agent type '{agent_type}' not in review list - skipping")
            return self._allow(f"Agent type '{agent_type}' not configured for review")

        self._global_logger.info(f"Agent type '{agent_type}' requires review")

        # Check if this is a retry and if we've hit max review cycles
        review_count = agent.completed_review_count
        max_cycles = config.settings.max_review_cycles

        if hook_input.stop_hook_active:
            # This is a retry after a previous block
            if review_count >= max_cycles:
                self._global_logger.warning(
                    f"Max review cycles ({max_cycles}) reached - allowing without re-review"
                )
                return self._allow(f"Max review cycles reached ({review_count}/{max_cycles})")

            self._global_logger.info(
                f"Retry detected (review {review_count + 1}/{max_cycles}) - re-reviewing to verify fix"
            )
        else:
            self._global_logger.info(f"Initial review (1/{max_cycles})")

        # Get the agent transcript path
        agent_transcript_path = hook_input.agent_transcript_path
        if not agent_transcript_path or not agent_transcript_path.exists():
            self._global_logger.warning("Agent transcript not found")
            return self._allow("Agent transcript not found")

        # Parse agent transcript for file changes
        analysis = self._parser_service.parse(agent_transcript_path)

        self._global_logger.info(f"Transcript entries: {analysis.entry_count}")
        self._global_logger.info(f"File changes: {analysis.file_change_count}")

        if not analysis.has_file_changes:
            self._global_logger.info("No file changes - nothing to review")
            return self._allow("No file changes")

        # Log file changes
        self._global_logger.info("Files changed:")
        for fc in analysis.file_changes:
            self._global_logger.info(f"  - {fc.path} ({fc.action.value})")

        # Skip if configured and no file changes
        if config.settings.skip_if_no_file_changes and not analysis.has_file_changes:
            self._global_logger.info("No file changes - skipping review per config")
            return self._allow("No file changes (skip_if_no_file_changes=true)")

        # Create review directory
        review_dir, review_number = self._session_storage.create_review_dir(
            session_id=hook_input.session_id,
            agent_id=hook_input.agent_id,
        )
        self._global_logger.info(f"Review #{review_number} starting")

        # Start tracking the review in session.json
        self._session_storage.start_agent_review(
            session_id=hook_input.session_id,
            agent_id=hook_input.agent_id,
        )

        # Set up review logger
        review_logger = ReviewLogger(
            review_dir=review_dir,
            review_number=review_number,
            agent_id=hook_input.agent_id,
            verbose=self._verbose,
        )

        # Get file paths for review
        file_paths = analysis.unique_file_paths
        review_logger.log_review_start(file_paths)

        # Run review
        review_start = time.time()
        review_result = self._reviewer_service.review(
            files=file_paths,
            original_task=analysis.initial_prompt,
        )
        review_duration_ms = int((time.time() - review_start) * 1000)

        # Log result
        decision = "allow" if review_result.passed else "block"
        review_logger.log_decision(decision, review_result.feedback)
        review_logger.log_review_end(review_duration_ms)
        review_logger.close()

        # Save review details (JSON)
        review_details = ReviewDetails(
            session_id=hook_input.session_id,
            agent_id=hook_input.agent_id,
            agent_type=agent_type,
            review_number=review_number,
            decision=decision,
            duration_ms=review_duration_ms,
            file_changes=[
                ReviewFileChange(
                    path=fc.path,
                    action=fc.action.value,
                    tool_name=fc.tool_name,
                    tool_input=fc.tool_input,
                )
                for fc in analysis.file_changes
            ],
        )
        review_details.save(review_dir)

        # Save review markdown
        review_context = ReviewContext(
            session_id=hook_input.session_id,
            agent_id=hook_input.agent_id,
            agent_type=agent_type,
            review_number=review_number,
            files_reviewed=file_paths,
            original_task=analysis.initial_prompt,
            result=review_result,
            duration_ms=review_duration_ms,
        )
        formatter = ReviewMarkdownFormatter()
        review_md_path = review_dir / "review.md"
        with open(review_md_path, "w") as f:
            f.write(formatter.format(review_context))

        self._global_logger.info(f"Review #{review_number} complete: {decision} ({review_duration_ms}ms)")
        self._global_logger.info(
            f"Review usage: {review_result.total_tokens} tokens "
            f"(in={review_result.input_tokens}, out={review_result.output_tokens}), "
            f"cost=${review_result.total_cost_usd or 0:.4f}"
        )

        # End the review with result and usage stats
        self._session_storage.end_agent_review(
            session_id=hook_input.session_id,
            agent_id=hook_input.agent_id,
            passed=review_result.passed,
            input_tokens=review_result.input_tokens,
            output_tokens=review_result.output_tokens,
            total_cost_usd=review_result.total_cost_usd,
        )

        if review_result.passed:
            return self._allow("Review passed")
        else:
            return self._block(review_result.feedback)

    def _allow(self, reason: str) -> HookResult:
        """Create an allow result."""
        return HookResult(decision="allow", reason=reason, should_block=False)

    def _block(self, reason: str) -> HookResult:
        """Create a block result."""
        return HookResult(decision="block", reason=reason, should_block=True)


def main() -> int:
    """Main entry point."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON input: {e}", file=sys.stderr)
        return 1

    verbose = os.environ.get("DEBUG") == "1"
    hook = SubagentReviewerHook(verbose=verbose)
    return hook.run(input_data)


if __name__ == "__main__":
    sys.exit(main())
