"""
Validation result model.
"""

from dataclasses import dataclass


@dataclass
class E2EPathValidationResult:
    """
    Result of validating an E2E test file path.

    Attributes:
        is_valid: True if the path follows conventions, False if it should be blocked
        reason: Explanation for blocking (only set when is_valid=False)
        error: Error message if validation failed due to technical issues
    """

    is_valid: bool
    reason: str | None = None
    error: str | None = None

    @property
    def should_block(self) -> bool:
        """Return True if the tool call should be blocked."""
        return not self.is_valid and self.error is None

    def to_hook_response(self) -> dict[str, str] | None:
        """
        Convert to Claude Code pre-tool hook response format.

        Returns:
            None if valid (allow the operation)
            {"decision": "block", "reason": "..."} if invalid
        """
        if self.is_valid:
            return None

        if self.error:
            # Technical error - don't block, just warn
            return None

        return {
            "decision": "block",
            "reason": self.reason or "Path does not follow E2E conventions.",
        }
