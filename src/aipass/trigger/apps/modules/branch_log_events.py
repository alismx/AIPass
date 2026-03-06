
# ===================AIPASS====================
# META DATA HEADER
# Name: branch_log_events.py - Branch Log Events Module
# Date: 2026-02-02
# Version: 1.0.0
# Category: trigger/modules
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-02-02): Created - FPLAN-0284 Phase 4
#
# CODE STANDARDS:
#   - Follows AIPass Seed standards
#   - Module orchestrates, handlers contain logic
#   - Public API for branch log event watching
# =============================================

"""
Branch Log Events Module - Public API for branch log watching

Provides start/stop/status commands for the branch log watcher.
Watches src/aipass/*/logs/*.log for ERROR entries.
Fires error_detected events handled by AI_Mail's error_handler.

Commands: start, stop, status
Architecture: Module orchestrates handlers
"""

import sys
from pathlib import Path


from aipass.prax.apps.modules.logger import system_logger as logger
from aipass.trigger.apps.modules.core import trigger

from aipass.trigger.apps.handlers.log_watcher import (
    set_event_callback,
    start_branch_log_watcher,
    stop_branch_log_watcher,
    is_branch_log_watcher_active,
    get_watcher_status,
    clear_seen_hashes
)
from aipass.trigger.apps.config import AIPASS_PKG_ROOT


def start() -> bool:
    """
    Start the branch log watcher.

    Watches src/aipass/*/logs/*.log for ERROR entries.
    Fires error_detected events to registered handlers.

    Returns:
        True if started successfully, False otherwise
    """
    logger.info("[TRIGGER] Starting branch log watcher")

    # Set the event callback to trigger.fire
    set_event_callback(trigger.fire)

    # Start the watcher
    observer = start_branch_log_watcher()
    if observer:
        logger.info(f"[TRIGGER] Branch log watcher started, monitoring: {AIPASS_PKG_ROOT}/*/logs/*.log")
        return True
    logger.error("[TRIGGER] Failed to start branch log watcher")
    return False


def stop() -> None:
    """
    Stop the branch log watcher.
    """
    logger.info("[TRIGGER] Stopping branch log watcher")
    stop_branch_log_watcher()
    logger.info("[TRIGGER] Branch log watcher stopped")


def status() -> dict:
    """
    Get branch log watcher status.

    Returns:
        Dict with status info from handler
    """
    return get_watcher_status()


def reset_hashes() -> None:
    """
    Clear the error deduplication hash set.

    Useful after extended runtime or for testing.
    """
    clear_seen_hashes()
    logger.info("[TRIGGER] Branch log watcher hash set cleared")


def print_help() -> None:
    """Print module help."""
    from aipass.cli.apps.modules import console

    console.print("Branch Log Events - Branch Log Watcher\n")
    console.print("USAGE:")
    console.print("  drone @trigger branch_log_events <command>")
    console.print("  python3 branch_log_events.py <command>\n")
    console.print("COMMANDS:")
    console.print("  start  - Start watching branch logs for errors")
    console.print("  stop   - Stop the branch log watcher")
    console.print("  status - Show watcher status")
    console.print("  reset  - Clear error deduplication hashes\n")
    console.print("MONITORING:")
    console.print(f"  Path: {AIPASS_PKG_ROOT}/*/logs/*.log")
    console.print("  Format: Prax log format (timestamp | module | LEVEL | message)\n")
    console.print("EVENTS FIRED:")
    console.print("  error_detected - When ERROR/CRITICAL level log detected")
    console.print("                   Handled by AI_Mail's error_handler\n")


def handle_command(command: str, args: list) -> bool:
    """
    Handle branch_log_events commands - orchestrate handler calls.

    Args:
        command: Module name or subcommand (branch_log_events, start, stop, status, reset)
        args: Additional arguments

    Returns:
        True if command was handled, False otherwise
    """
    from aipass.cli.apps.modules import console

    # Handle module-name routing (drone @trigger branch_log_events <subcmd>)
    if command == "branch_log_events":
        if not args:
            print_help()
            return True
        subcommand = args[0]
        remaining = args[1:]
        return handle_command(subcommand, remaining)

    # Handle direct subcommands
    if command not in ["start", "stop", "status", "reset"]:
        return False

    if args and args[0] in ['--help', '-h', 'help']:
        print_help()
        return True

    if command == "start":
        if start():
            console.print("✅ Branch log watcher started")
            console.print(f"   Monitoring: {AIPASS_PKG_ROOT}/*/logs/*.log")
            console.print("   Events: error_detected → AI_Mail error_handler")
        else:
            console.print("❌ Failed to start branch log watcher")
            console.print("   Check if watchdog package is installed")
    elif command == "stop":
        stop()
        console.print("✅ Branch log watcher stopped")
    elif command == "status":
        info = status()
        console.print("Branch Log Watcher Status")
        console.print(f"  Active: {info['active']}")
        console.print(f"  Watchdog available: {info['watchdog_available']}")
        console.print(f"  Seen error hashes: {info['seen_hashes_count']}")
        console.print(f"  AIPASS root: {info['aipass_root']}")
    elif command == "reset":
        reset_hashes()
        console.print("✅ Error deduplication hashes cleared")

    return True


if __name__ == "__main__":
    import argparse
    from aipass.cli.apps.modules import console

    if len(sys.argv) == 1 or sys.argv[1] in ['--help', '-h', 'help']:
        print_help()
        sys.exit(0)

    parser = argparse.ArgumentParser(description='Branch Log Events Module')
    parser.add_argument('command', choices=['start', 'stop', 'status', 'reset'])
    parsed_args = parser.parse_args()

    handle_command(parsed_args.command, sys.argv[2:])
