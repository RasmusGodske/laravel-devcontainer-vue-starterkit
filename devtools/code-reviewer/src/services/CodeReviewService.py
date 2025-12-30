"""
Code review service using Claude Agent SDK.
"""

import re
import time
from datetime import datetime
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

from ..loggers import CodeReviewLogger
from ..models import CodeReviewOptions, CodeReviewResult


class CodeReviewService:
    """
    Runs code reviews using Claude Agent SDK.

    The service is configured with options and a logger, then runs reviews
    on files. The prompt template controls what the review checks.

    Example:
        options = CodeReviewOptions(
            prompt_template_path=Path("prompt.md"),
            cwd=Path("/path/to/project"),
        )
        logger = CodeReviewLogger(session_id, log_path)

        service = CodeReviewService(options, logger)
        result = await service.review(
            files="app/Models/User.php",
            original_task="Added user model",
        )
    """

    def __init__(
        self,
        options: CodeReviewOptions,
        logger: CodeReviewLogger,
    ) -> None:
        """
        Initialize the review service.

        Args:
            options: Review configuration
            logger: Session logger for recording review activity
        """
        self._options = options
        self._logger = logger
        self._template: str | None = None

    @property
    def template(self) -> str:
        """Load and cache the prompt template."""
        if self._template is None:
            self._template = self._load_template()
        return self._template

    def _load_template(self) -> str:
        """Load the prompt template from disk."""
        path = self._options.prompt_template_path
        if not path.exists():
            raise FileNotFoundError(
                f"Prompt template not found: {path}\n"
                f"Create the template file or check the path."
            )
        return path.read_text()

    def _format_prompt(self, **kwargs: str) -> str:
        """
        Format the prompt template with placeholders.

        Unknown placeholders are left unchanged (no KeyError).
        """

        class SafeDict(dict):  # type: ignore[type-arg]
            def __missing__(self, key: str) -> str:
                return f"{{{key}}}"

        return self.template.format_map(SafeDict(**kwargs))

    async def review(
        self,
        files: str,
        original_task: str = "",
    ) -> CodeReviewResult:
        """
        Run a code review on the given files.

        Args:
            files: String describing files to review
            original_task: Description of what was being done (context)

        Returns:
            CodeReviewResult with findings
        """
        self._logger.info(f"Starting review for: {files}")
        self._logger.info(f"Task context: {original_task or '(none)'}")

        started_at = datetime.now()
        start_time = time.monotonic()

        # Format the prompt
        prompt = self._format_prompt(
            files=files,
            original_task=original_task or "No task description available.",
        )

        # Configure the Claude agent
        agent_options = ClaudeAgentOptions(
            max_turns=self._options.max_turns,
            cwd=str(self._options.cwd),
            allowed_tools=self._options.allowed_tools,
            mcp_servers=self._options.mcp_servers if self._options.mcp_servers else {},
        )

        if self._options.mcp_servers:
            mcp_names = list(self._options.mcp_servers.keys())
            self._logger.debug(f"MCP servers: {mcp_names}")

        self._logger.debug(f"Agent options: max_turns={self._options.max_turns}")

        # Run the review
        review_texts: list[str] = []
        message_count = 0
        tool_call_count = 0
        total_cost_usd: float | None = None
        error_message: str | None = None

        # Track usage per message ID (same ID = same usage, only count once)
        processed_message_ids: set[str] = set()
        accumulated_input_tokens = 0
        accumulated_output_tokens = 0
        accumulated_cache_creation = 0
        accumulated_cache_read = 0

        try:
            async for message in query(prompt=prompt, options=agent_options):
                message_count += 1
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            review_texts.append(block.text)
                        else:
                            # Track tool calls
                            tool_call_count += 1

                    # Track usage from AssistantMessage (deduplicated by message ID)
                    message_id = getattr(message, "id", None)
                    if message_id and message_id not in processed_message_ids:
                        processed_message_ids.add(message_id)
                        usage = getattr(message, "usage", None)
                        if usage:
                            self._logger.debug(f"Usage from message {message_id}: {usage}")
                            accumulated_input_tokens += usage.get("input_tokens", 0)
                            accumulated_output_tokens += usage.get("output_tokens", 0)
                            accumulated_cache_creation += usage.get("cache_creation_input_tokens", 0)
                            accumulated_cache_read += usage.get("cache_read_input_tokens", 0)

                elif isinstance(message, ResultMessage):
                    # ResultMessage.total_cost_usd is authoritative for cost
                    total_cost_usd = message.total_cost_usd
                    self._logger.debug(f"ResultMessage total_cost_usd: {total_cost_usd}")

        except Exception as e:
            error_message = f"Claude Agent SDK error: {type(e).__name__}: {e}"
            self._logger.error(error_message)

        completed_at = datetime.now()
        duration_ms = int((time.monotonic() - start_time) * 1000)

        # Calculate final token counts (include cache tokens in input)
        input_tokens = accumulated_input_tokens + accumulated_cache_creation + accumulated_cache_read
        output_tokens = accumulated_output_tokens
        total_tokens = input_tokens + output_tokens

        self._logger.info(
            f"Review completed: messages={message_count}, "
            f"tool_calls={tool_call_count}, tokens={total_tokens}, duration={duration_ms}ms"
        )
        self._logger.debug(
            f"Token breakdown: input={accumulated_input_tokens}, output={output_tokens}, "
            f"cache_creation={accumulated_cache_creation}, cache_read={accumulated_cache_read}"
        )

        # Handle errors
        if error_message:
            return CodeReviewResult(
                has_issues=False,  # Don't block on SDK errors
                review_text=f"Review failed: {error_message}",
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=duration_ms,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_cost_usd=total_cost_usd,
            )

        # Combine text blocks
        review_text = "\n\n".join(review_texts) if review_texts else ""

        # Handle empty output
        if not review_text.strip():
            self._logger.warning("Review completed with empty output")
            return CodeReviewResult(
                has_issues=False,
                review_text="Review completed but no output was generated.",
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=duration_ms,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_cost_usd=total_cost_usd,
            )

        # Parse decision from review output
        has_issues = self._parse_decision(review_text)
        decision = "blocked" if has_issues else "passed"
        self._logger.info(f"Review decision: {decision}")

        return CodeReviewResult(
            has_issues=has_issues,
            review_text=review_text,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_cost_usd=total_cost_usd,
        )

    @staticmethod
    def _parse_decision(review_text: str) -> bool:
        """
        Parse the decision from review output using XML tags.

        The prompt instructs the reviewer to output:
        - <decision>passed</decision> for no issues
        - <decision>blocked</decision> for issues found

        Returns:
            True if issues were found (blocked), False if passed
        """
        # Look for <decision>...</decision> tag
        match = re.search(
            r"<decision>\s*(passed|blocked)\s*</decision>",
            review_text,
            re.IGNORECASE,
        )

        if match:
            decision = match.group(1).lower()
            return decision == "blocked"

        # Also check for <review_result> wrapper format
        match = re.search(
            r"<review_result>.*?<decision>\s*(passed|blocked)\s*</decision>.*?</review_result>",
            review_text,
            re.IGNORECASE | re.DOTALL,
        )
        if match:
            decision = match.group(1).lower()
            return decision == "blocked"

        # Default to passing if no XML tag found
        return False
