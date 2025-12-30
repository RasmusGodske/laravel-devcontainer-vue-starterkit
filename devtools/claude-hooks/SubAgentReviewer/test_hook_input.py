#!/usr/bin/env python3
"""
Test script to capture and log hook input.

Use this to discover what data different hooks provide.
Logs to test_hook_input.log in the same directory.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent / "test_hook_input.log"


def main() -> int:
    """Capture stdin and log it."""
    timestamp = datetime.now().isoformat()

    try:
        input_data = json.load(sys.stdin)
        input_json = json.dumps(input_data, indent=2)
    except json.JSONDecodeError as e:
        input_json = f"Invalid JSON: {e}"
    except Exception as e:
        input_json = f"Error reading stdin: {e}"

    # Log to file
    with open(LOG_FILE, "a") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"{'='*60}\n")
        f.write(input_json)
        f.write("\n")

    # Don't block - just observe
    return 0


if __name__ == "__main__":
    sys.exit(main())
