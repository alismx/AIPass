# =================== AIPass ====================
# Name: claude.py
# Version: 1.0.0
# Description: Claude Code bridge — entry point for provider hook settings
# Branch: hooks
# Layer: apps/handlers/bridges
# Created: 2026-05-18
# Modified: 2026-05-18
# =============================================

"""
Claude Code bridge.

Thin entry point called from ~/.claude/settings.json hook entries.
Normalizes Claude Code's stdin/stdout format and calls the engine.

Called from provider settings as the sole hook entry point per event type.
"""

import sys

from aipass.hooks.apps.modules.engine import dispatch, find_project_config
from aipass.prax.apps.modules.logger import system_logger as logger


def main() -> None:
    """Entry point — receive event type from Claude Code, dispatch via engine."""
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: claude.py <EventType>\n")
        sys.exit(1)

    event_type = sys.argv[1]

    stdin_data = ""
    if not sys.stdin.isatty():
        stdin_data = sys.stdin.read()

    config = find_project_config()
    if config is None:
        config = {"hooks_enabled": True}
        logger.info("[HOOKS:claude] no project config found, using defaults")

    output = dispatch(event_type, stdin_data, config)
    if output:
        sys.stdout.write(output)


if __name__ == "__main__":
    main()
