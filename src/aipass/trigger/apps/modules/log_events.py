#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: log_events.py - Log Events Module
# Date: 2026-01-31
# Version: 1.0.0
# Category: trigger/modules
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-01-31): Created - Phase 2 migration (FPLAN-0279)
#
# CODE STANDARDS:
#   - Follows AIPass Seed standards
#   - Module orchestrates, handlers contain logic
#   - Public API for log event watching
# =============================================

"""
Log Events Module - Public API for log event watching

Provides start/stop/status commands for the centralized log watcher.
Trigger owns all log event detection - other branches respond to events.

Commands: start, stop, status
Architecture: Module orchestrates handlers
"""

import sys
from pathlib import Path


from aipass.prax.apps.modules.logger import system_logger as logger

# Import handler functions
from aipass.trigger.apps.handlers.watchers.log_watcher import (
    start_log_watcher,
    stop_log_watcher,
    is_log_watcher_active,
    SYSTEM_LOGS_DIR
)


def start() -> bool:
    """
    Start the centralized log watcher.

    Watches /home/aipass/system_logs for log file changes.
    Fires error_logged and warning_logged events.

    Returns:
        True if started successfully, False otherwise
    """
    logger.info("[TRIGGER] Starting log watcher")
    observer = start_log_watcher()
    if observer:
        logger.info(f"[TRIGGER] Log watcher started, monitoring: {SYSTEM_LOGS_DIR}")
        return True
    logger.error("[TRIGGER] Failed to start log watcher")
    return False


def stop() -> None:
    """
    Stop the centralized log watcher.
    """
    logger.info("[TRIGGER] Stopping log watcher")
    stop_log_watcher()
    logger.info("[TRIGGER] Log watcher stopped")


def status() -> dict:
    """
    Get log watcher status.

    Returns:
        Dict with status info:
        {
            'active': bool,
            'log_dir': str
        }
    """
    return {
        'active': is_log_watcher_active(),
        'log_dir': str(SYSTEM_LOGS_DIR)
    }


def print_help() -> None:
    """Print module help."""
    from aipass.cli.apps.modules import console

    console.print("Log Events - Centralized Log Watcher\n")
    console.print("USAGE:")
    console.print("  drone trigger log_events <command>")
    console.print("  python3 log_events.py <command>\n")
    console.print("COMMANDS:")
    console.print("  start  - Start watching logs for errors/warnings")
    console.print("  stop   - Stop the log watcher")
    console.print("  status - Show watcher status\n")
    console.print("EVENTS FIRED:")
    console.print("  error_logged   - When ERROR level log detected")
    console.print("  warning_logged - When WARNING level log detected\n")


def handle_command(command: str, args: list) -> bool:
    """
    Handle log_events commands - orchestrate handler calls.

    Args:
        command: Command to execute (start, stop, status)
        args: Additional arguments

    Returns:
        True if command was handled, False otherwise
    """
    from aipass.cli.apps.modules import console

    if command not in ["start", "stop", "status"]:
        return False

    if args and args[0] in ['--help', '-h', 'help']:
        print_help()
        return True

    if command == "start":
        if start():
            console.print("✅ Log watcher started")
            console.print(f"   Monitoring: {SYSTEM_LOGS_DIR}")
        else:
            console.print("❌ Failed to start log watcher")
    elif command == "stop":
        stop()
        console.print("✅ Log watcher stopped")
    elif command == "status":
        info = status()
        console.print("Log Watcher Status")
        console.print(f"  Active: {info['active']}")
        console.print(f"  Log dir: {info['log_dir']}")

    return True


if __name__ == "__main__":
    import argparse
    from aipass.cli.apps.modules import console

    if len(sys.argv) == 1 or sys.argv[1] in ['--help', '-h', 'help']:
        print_help()
        sys.exit(0)

    parser = argparse.ArgumentParser(description='Log Events Module')
    parser.add_argument('command', choices=['start', 'stop', 'status'])
    parsed_args = parser.parse_args()

    handle_command(parsed_args.command, sys.argv[2:])
