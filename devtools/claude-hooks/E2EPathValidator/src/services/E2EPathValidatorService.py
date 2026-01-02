"""
E2E path validation service using Claude Agent SDK.
"""

import re
import sys
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    TextBlock,
    query,
)

from ..models import E2EPathValidationResult


class E2EPathValidatorService:
    """
    Validates E2E test file paths using Claude Agent SDK.

    The service spawns a Claude agent to check if the test path
    follows the project's conventions (typically mirroring the pages structure).

    Example:
        service = E2EPathValidatorService(
            prompt_template_path=Path("prompt.md"),
            project_root=Path("/path/to/project"),
        )
        result = await service.validate("e2e/tests/Feature/Users/Index/smoke.spec.ts")
    """

    # Tools needed for path validation
    ALLOWED_TOOLS = [
        "Read",
        "Glob",
        "Grep",
    ]

    def __init__(
        self,
        prompt_template_path: Path,
        project_root: Path,
        max_turns: int = 10,
        verbose: bool = False,
    ) -> None:
        """
        Initialize the validation service.

        Args:
            prompt_template_path: Path to the prompt template file
            project_root: Project root directory for running commands
            max_turns: Maximum number of tool calls the agent can make
            verbose: Whether to print debug output
        """
        self._prompt_template_path = prompt_template_path
        self._project_root = project_root
        self._max_turns = max_turns
        self._verbose = verbose
        self._template: str | None = None

    @property
    def template(self) -> str:
        """Load and cache the prompt template."""
        if self._template is None:
            self._template = self._load_template()
        return self._template

    def _load_template(self) -> str:
        """Load the prompt template from disk."""
        if not self._prompt_template_path.exists():
            raise FileNotFoundError(
                f"Prompt template not found: {self._prompt_template_path}"
            )
        return self._prompt_template_path.read_text()

    def _format_prompt(self, file_path: str) -> str:
        """Format the prompt template with the file path."""
        return self.template.replace("{file_path}", file_path)

    def _log(self, message: str) -> None:
        """Log a message to stderr if verbose mode is enabled."""
        if self._verbose:
            print(f"[E2EPathValidator] {message}", file=sys.stderr)

    async def validate(self, file_path: str) -> E2EPathValidationResult:
        """
        Validate an E2E test file path.

        Args:
            file_path: The E2E test file path being created/edited

        Returns:
            E2EPathValidationResult indicating if the path is valid
        """
        self._log(f"Validating path: {file_path}")

        # Format the prompt
        prompt = self._format_prompt(file_path)

        # Configure the Claude agent
        agent_options = ClaudeAgentOptions(
            max_turns=self._max_turns,
            cwd=str(self._project_root),
            allowed_tools=self.ALLOWED_TOOLS,
        )

        self._log(f"Running agent with max_turns={self._max_turns}")

        # Collect response text
        response_texts: list[str] = []

        try:
            async for message in query(prompt=prompt, options=agent_options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            response_texts.append(block.text)

        except Exception as e:
            error_msg = f"Claude Agent SDK error: {type(e).__name__}: {e}"
            self._log(error_msg)
            return E2EPathValidationResult(
                is_valid=True,  # Don't block on SDK errors
                error=error_msg,
            )

        # Combine response text
        response_text = "\n".join(response_texts)

        if not response_text.strip():
            self._log("Empty response from agent")
            return E2EPathValidationResult(
                is_valid=True,  # Don't block on empty response
                error="Validation completed but no output was generated.",
            )

        # Parse the decision
        return self._parse_response(response_text)

    def _parse_response(self, response_text: str) -> E2EPathValidationResult:
        """
        Parse the validation response from Claude.

        Looks for:
        - <validation_result><decision>allow</decision></validation_result>
        - <validation_result><decision>block</decision><reason>...</reason></validation_result>

        Returns:
            E2EPathValidationResult based on the parsed decision
        """
        # Look for <decision>...</decision> tag
        decision_match = re.search(
            r"<decision>\s*(allow|block)\s*</decision>",
            response_text,
            re.IGNORECASE,
        )

        if decision_match:
            decision = decision_match.group(1).lower()

            if decision == "allow":
                self._log("Decision: ALLOW")
                return E2EPathValidationResult(is_valid=True)

            # Decision is "block" - extract reason
            reason_match = re.search(
                r"<reason>(.*?)</reason>",
                response_text,
                re.IGNORECASE | re.DOTALL,
            )
            reason = reason_match.group(1).strip() if reason_match else None

            self._log(f"Decision: BLOCK - {reason}")
            return E2EPathValidationResult(
                is_valid=False,
                reason=reason or "Path does not follow E2E conventions.",
            )

        # Fallback: check for ALLOW/BLOCK keywords
        response_upper = response_text.upper()
        if "BLOCK" in response_upper:
            # Try to extract some context
            self._log("Decision: BLOCK (keyword fallback)")
            return E2EPathValidationResult(
                is_valid=False,
                reason=response_text[:500],  # Use first 500 chars as reason
            )

        if "ALLOW" in response_upper:
            self._log("Decision: ALLOW (keyword fallback)")
            return E2EPathValidationResult(is_valid=True)

        # Default: allow (don't block on unexpected response format)
        self._log(f"Unexpected response format, defaulting to ALLOW: {response_text[:100]}")
        return E2EPathValidationResult(
            is_valid=True,
            error=f"Unexpected response format: {response_text[:100]}",
        )
