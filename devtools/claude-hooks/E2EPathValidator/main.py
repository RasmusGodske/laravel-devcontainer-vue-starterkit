#!/usr/bin/env python3
"""
E2EPathValidator - Pre-tool hook to validate E2E test file paths.

Uses Claude Agent SDK to validate that E2E test paths follow
the project's conventions (typically mirroring the pages/views structure).

Usage (called automatically by Claude Code):
    echo '{"tool": "Write", "input": {"file_path": "..."}}' | python3 main.py

Output:
- Exit 0 with no JSON: Allow tool to proceed
- Exit 0 with {"decision": "block", "reason": "..."}: Block with feedback
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from src.services import E2EPathValidatorService

# Pattern to identify E2E test files (configurable via env var)
E2E_TEST_PATTERN = os.environ.get("E2E_TEST_PATTERN", "e2e/tests/")

# Path to the prompt template (relative to this file)
VALIDATOR_DIR = Path(__file__).parent.resolve()
PROMPT_PATH = VALIDATOR_DIR / "prompt.md"


def is_e2e_test_file(file_path: str) -> bool:
    """Check if the file path is an E2E test file."""
    return E2E_TEST_PATTERN in file_path and file_path.endswith(".spec.ts")


def get_project_root() -> Path:
    """Get the project root directory from environment or infer from hook location."""
    if "CLAUDE_PROJECT_DIR" in os.environ:
        return Path(os.environ["CLAUDE_PROJECT_DIR"])
    # Fallback: hook is at devtools/claude-hooks/E2EPathValidator/main.py
    return VALIDATOR_DIR.parent.parent.parent


async def validate_path(file_path: str, project_root: Path, verbose: bool) -> dict[str, str] | None:
    """
    Validate the E2E test path using Claude Agent SDK.

    Returns:
        None if valid (allow the operation)
        {"decision": "block", "reason": "..."} if invalid
    """
    service = E2EPathValidatorService(
        prompt_template_path=PROMPT_PATH,
        project_root=project_root,
        verbose=verbose,
    )

    result = await service.validate(file_path)
    return result.to_hook_response()


def main() -> int:
    """Main entry point."""
    verbose = os.environ.get("E2E_VALIDATOR_VERBOSE", "").lower() in ("1", "true", "yes")

    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        if verbose:
            print(f"Warning: Invalid JSON input: {e}", file=sys.stderr)
        return 0

    # Extract file path from tool input
    tool_input = input_data.get("input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        return 0

    # Only validate E2E test files
    if not is_e2e_test_file(file_path):
        return 0

    project_root = get_project_root()

    # Run validation
    try:
        response = asyncio.run(validate_path(file_path, project_root, verbose))

        if response:
            print(json.dumps(response))

    except Exception as e:
        if verbose:
            print(f"Warning: Validation failed: {e}", file=sys.stderr)
        # Fail open - don't block on errors
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
