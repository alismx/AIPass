#!/usr/bin/env python3
"""PostToolUse hook — reminds agent to arm watchdog after dispatch.

Fires after Bash commands containing 'drone @ai_mail dispatch'.
Outputs additionalContext telling the agent to arm the watchdog.
Skips if watchdog is already part of the same command.

Version: 1.0.0
"""

import json
import sys


def main():
    """Check if dispatch was run and remind to arm watchdog."""
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    if tool_name != "Bash":
        return

    command = tool_input.get("command", "")

    # Only trigger on dispatch commands
    if "drone @ai_mail dispatch" not in command:
        return

    # Skip if watchdog is already in the same command
    if "unread_count" in command and "while [" in command:
        return

    # Skip if it's just checking dispatch status (not sending)
    if "dispatch wake" in command and "dispatch @" not in command:
        return

    result = {
        "additionalContext": (
            "[AUTO-WATCHDOG] Dispatch detected — arm watchdog NOW. "
            "Run the watchdog one-liner from your local prompt with "
            "run_in_background: true and timeout: 600000."
        )
    }
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
