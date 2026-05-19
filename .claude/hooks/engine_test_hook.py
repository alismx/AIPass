# =================== AIPass ====================
# Name: engine_test_hook.py
# Description: Test hook for engine POC — proves engine dispatch works
# Version: 0.1.0
# Created: 2026-05-17
# Modified: 2026-05-17
# =============================================

"""
Test hook that proves the engine dispatched correctly.
Writes a timestamped entry to engine_test.log and outputs a system reminder.
Safe — no side effects beyond logging.
"""

import json
import os
import sys
import time
from pathlib import Path

LOG_FILE = Path(os.environ.get("AIPASS_HOME", "")) / ".claude" / "hooks" / "engine_test.log"


def main() -> None:
    """Log proof of execution and output a system reminder."""
    stdin_data = ""
    if not sys.stdin.isatty():
        stdin_data = sys.stdin.read()

    event_info = {}
    try:
        if stdin_data.strip():
            event_info = json.loads(stdin_data)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"engine_test_hook: parse error: {exc}\n")

    entry = {
        "ts": time.time(),
        "hook": "engine_test_hook",
        "cwd": str(Path.cwd()),
        "event_keys": list(event_info.keys())[:5],
    }

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError as exc:
        sys.stderr.write(f"engine_test_hook: log failed: {exc}\n")

    sys.stdout.write("ENGINE_TEST: Hook engine dispatched successfully\n")


if __name__ == "__main__":
    main()
