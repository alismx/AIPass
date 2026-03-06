
# ===================AIPASS====================
# META DATA HEADER
# Name: telegram_bot.py - Telegram multi-bot module (replaces telegram_bridge.py + telegram_chat.py)
# Date: 2026-02-24
# Version: 1.0.0
# Category: api/modules
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-02-24): Initial - unified multi-bot public API module
#
# CODE STANDARDS:
#   - Module layer: thin orchestration over handler functions
#   - This is the PUBLIC API that other branches import from
#   - Replaces telegram_bridge.py and telegram_chat.py
# =============================================

"""
Telegram Multi-Bot Module - Public API

Unified entry point for the AIPass multi-bot Telegram architecture.
Re-exports all handler internals so other branches can import them
without triggering the cross-branch handler guard.

Replaces:
  - telegram_bridge.py (bridge operations)
  - telegram_chat.py (direct chat + standards re-exports)

Usage from other branches:
    from aipass.api.apps.modules.telegram_bot import BaseBot, BranchPlugin
    from aipass.api.apps.modules.telegram_bot import create_bot, delete_bot
    from aipass.api.apps.modules.telegram_bot import list_bots, get_bot
    from aipass.api.apps.modules.telegram_bot import load_bot_config
    from aipass.api.apps.modules.telegram_bot import (
        STANDARD_COMMANDS, build_help_text, build_welcome_text,
        build_status_text, parse_command, handle_standard_command,
    )
"""

# Infrastructure
import sys
from pathlib import Path

# Prax logger and CLI utilities
from aipass.prax.apps.modules.logger import system_logger as logger
from aipass.cli.apps.modules import console, header, success, error, warning

# Handler imports (operations)
from aipass.api.apps.handlers.telegram import bot_operations

# =============================================
# RE-EXPORTS FROM HANDLERS (Public API)
# =============================================

from aipass.api.apps.handlers.telegram.base_bot import BaseBot
from aipass.api.apps.handlers.telegram.branch_plugin import BranchPlugin
from aipass.api.apps.handlers.telegram.bot_registry import (
    list_bots,
    get_bot,
    register_bot,
    get_bot_by_branch,
)
from aipass.api.apps.handlers.telegram.bot_factory import create_bot, delete_bot
from aipass.api.apps.handlers.telegram.config import load_bot_config
from aipass.api.apps.handlers.telegram.telegram_standards import (
    STANDARD_COMMANDS,
    PROCESSING_MSG,
    build_help_text,
    build_welcome_text,
    build_status_text,
    build_botfather_commands,
    parse_command,
    handle_standard_command,
)

# =============================================
# MODULE INTROSPECTION
# =============================================


def print_introspection() -> None:
    """Show module introspection - connected handlers and capabilities"""
    console.print()
    header("Telegram Multi-Bot Module Introspection")
    console.print()

    console.print("[cyan]Purpose:[/cyan] Multi-bot Telegram architecture for AIPass")
    console.print()

    console.print("[cyan]Connected Handlers:[/cyan]")
    console.print("  - api.apps.handlers.telegram.base_bot")
    console.print("  - api.apps.handlers.telegram.branch_plugin")
    console.print("  - api.apps.handlers.telegram.bot_registry")
    console.print("  - api.apps.handlers.telegram.bot_factory")
    console.print("  - api.apps.handlers.telegram.bot_operations")
    console.print("  - api.apps.handlers.telegram.config")
    console.print("  - api.apps.handlers.telegram.telegram_standards")
    console.print()

    console.print("[cyan]Available Commands:[/cyan]")
    console.print("  - start <bot_id>     - Start a specific bot (polling loop)")
    console.print("  - stop <bot_id>      - Stop a bot's systemd service")
    console.print("  - status [bot_id]    - Show bot status (single or all)")
    console.print("  - list               - List all registered bots")
    console.print("  - create <bot_id> <token> [options]  - Create new bot")
    console.print("  - delete <bot_id>    - Delete a bot")
    console.print()


def print_help() -> None:
    """Print module help with argparse"""
    import argparse

    parser = argparse.ArgumentParser(
        prog="python3 telegram_bot.py",
        description="Telegram Multi-Bot Module - AIPass multi-bot management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
COMMANDS:
  start <bot_id>                    - Start a bot (long-polling, blocks)
  stop <bot_id>                     - Stop a bot's systemd service
  status [bot_id]                   - Show bot status (single or all)
  list                              - List all registered bots
  create <bot_id> <token> [opts]    - Create a new bot
  delete <bot_id>                   - Delete a bot

CREATE OPTIONS:
  --branch <name>                   - Associate with an AIPass branch
  --work-dir <path>                 - Working directory for Claude sessions

EXAMPLES:
  # Start a bot (blocks until Ctrl+C)
  python3 telegram_bot.py start dev_central

  # Check all bot statuses
  python3 telegram_bot.py status

  # Create a new branch bot
  python3 telegram_bot.py create dev_central 123:ABC --branch dev_central

  # List all bots
  python3 telegram_bot.py list
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    start_p = subparsers.add_parser("start", help="Start a bot")
    start_p.add_argument("bot_id", help="Bot identifier")

    stop_p = subparsers.add_parser("stop", help="Stop a bot's systemd service")
    stop_p.add_argument("bot_id", help="Bot identifier")

    status_p = subparsers.add_parser("status", help="Show bot status")
    status_p.add_argument("bot_id", nargs="?", help="Bot identifier (optional)")

    subparsers.add_parser("list", help="List all registered bots")

    create_p = subparsers.add_parser("create", help="Create a new bot")
    create_p.add_argument("bot_id", help="Bot identifier")
    create_p.add_argument("token", help="Telegram bot token")
    create_p.add_argument("--branch", help="AIPass branch name")
    create_p.add_argument("--work-dir", help="Working directory")

    delete_p = subparsers.add_parser("delete", help="Delete a bot")
    delete_p.add_argument("bot_id", help="Bot identifier")

    console.print(parser.format_help())


# =============================================
# COMMAND HANDLING
# =============================================


def handle_command(command: str, args: list) -> bool:
    """
    Handle module commands routed via drone.

    Args:
        command: Command name (e.g., "telegram_bot")
        args: Command arguments

    Returns:
        True if command was handled, False to pass through
    """
    if not args:
        return False

    subcommand = args[0]

    if subcommand == "start" and len(args) >= 2:
        _cmd_start(args[1])
        return True

    elif subcommand == "stop" and len(args) >= 2:
        _cmd_stop(args[1])
        return True

    elif subcommand == "status":
        bot_id = args[1] if len(args) >= 2 else None
        _cmd_status(bot_id)
        return True

    elif subcommand == "list":
        _cmd_list()
        return True

    elif subcommand == "create" and len(args) >= 3:
        _cmd_create(args[1:])
        return True

    elif subcommand == "delete" and len(args) >= 2:
        _cmd_delete(args[1])
        return True

    elif subcommand == "help":
        print_help()
        return True

    return False


# =============================================
# THIN ORCHESTRATION (delegates to bot_operations handler)
# =============================================


def _cmd_start(bot_id: str) -> None:
    """Orchestrate bot start: header, delegate, exit."""
    header(f"Starting Bot: {bot_id}")
    console.print()

    config = load_bot_config(bot_id)
    if not config:
        error(f"No config found for bot '{bot_id}'")
        console.print("[dim]Expected: ~/.aipass/telegram_bots/{bot_id}.json[/dim]")
        return

    if not config.get("bot_token"):
        error(f"No bot_token in config for '{bot_id}'")
        return

    bot_name = config.get("bot_name", f"AIPass {bot_id} Bot")
    logger.info("Starting bot '%s' (%s)", bot_id, bot_name)
    success(f"Launching {bot_name}...")
    console.print()

    exit_code = bot_operations.start_bot(bot_id)
    if exit_code is None:
        error(f"Bot '{bot_id}' failed to start")
    else:
        sys.exit(exit_code)


def _cmd_stop(bot_id: str) -> None:
    """Orchestrate bot stop: header, delegate, display result."""
    header(f"Stopping Bot: {bot_id}")
    console.print()

    ok, msg = bot_operations.stop_bot(bot_id)
    if ok:
        logger.info("Stopped bot '%s'", bot_id)
        success(msg)
    else:
        logger.warning("Failed to stop bot '%s': %s", bot_id, msg)
        error(msg)

    console.print()


def _cmd_status(bot_id: str | None = None) -> None:
    """Orchestrate status display: header, delegate, format."""
    if bot_id:
        header(f"Bot Status: {bot_id}")
    else:
        header("All Bots Status")
    console.print()

    bots = bot_operations.get_status(bot_id)
    if not bots:
        if bot_id:
            error(f"Bot '{bot_id}' not found in registry")
        else:
            warning("No bots registered")
            console.print("[dim]Use 'create' to add a new bot[/dim]")
        console.print()
        return

    for bot in bots:
        for line in bot_operations.format_bot_details(bot):
            console.print(f"  [cyan]{line}[/cyan]")
        console.print()


def _cmd_list() -> None:
    """Orchestrate bot listing: header, delegate, format."""
    header("Registered Bots")
    console.print()

    bots = bot_operations.get_all_bots()
    if not bots:
        warning("No bots registered")
        console.print("[dim]Use 'create' to add a new bot[/dim]")
        console.print()
        return

    for line in bot_operations.format_bot_table(bots):
        console.print(line)
    console.print()


def _cmd_create(args: list) -> None:
    """Orchestrate bot creation: parse args, delegate, display result."""
    parsed = bot_operations.parse_create_args(args)
    if not parsed:
        error("Usage: create <bot_id> <token> [--branch <name>] [--work-dir <path>]")
        return

    bot_id = parsed["bot_id"]
    header(f"Creating Bot: {bot_id}")
    console.print()

    result = create_bot(
        bot_id=bot_id,
        bot_token=parsed["bot_token"],
        branch_name=parsed["branch_name"],
        work_dir=parsed["work_dir"],
    )

    if result:
        logger.info("Bot created via module: %s", bot_id)
        success(f"Bot '{bot_id}' created successfully")
        console.print()
        details = bot_operations.format_bot_details({
            "bot_id": result["bot_id"],
            "username": result["username"],
            "branch_name": result.get("branch_name"),
            "work_dir": result["work_dir"],
            "status": "active",
            "service_name": result["service_name"],
        })
        for line in details:
            console.print(f"  [cyan]{line}[/cyan]")
    else:
        logger.warning("Bot creation failed for '%s'", bot_id)
        error(f"Failed to create bot '{bot_id}'. Check logs for details.")

    console.print()


def _cmd_delete(bot_id: str) -> None:
    """Orchestrate bot deletion: verify, delegate, display result."""
    header(f"Deleting Bot: {bot_id}")
    console.print()

    bot = get_bot(bot_id)
    if not bot:
        error(f"Bot '{bot_id}' not found in registry")
        console.print()
        return

    result = delete_bot(bot_id)

    if result:
        logger.info("Bot deleted via module: %s", bot_id)
        success(f"Bot '{bot_id}' deleted successfully")
    else:
        logger.warning("Bot deletion failed for '%s'", bot_id)
        error(f"Failed to delete bot '{bot_id}'. Check logs for details.")

    console.print()


# =============================================
# STANDALONE EXECUTION
# =============================================

if __name__ == "__main__":
    """Standalone execution mode"""
    args = sys.argv[1:]

    # Show introspection when run without arguments
    if len(args) == 0:
        print_introspection()
        sys.exit(0)

    # Show help for explicit help flags
    if args[0] in ['--help', '-h', 'help']:
        print_help()
        sys.exit(0)

    # Execute command directly (standalone mode, not drone-routed)
    command = args[0]

    if command == "start" and len(args) >= 2:
        _cmd_start(args[1])
    elif command == "stop" and len(args) >= 2:
        _cmd_stop(args[1])
    elif command == "status":
        bot_id = args[1] if len(args) >= 2 else None
        _cmd_status(bot_id)
    elif command == "list":
        _cmd_list()
    elif command == "create" and len(args) >= 3:
        _cmd_create(args[1:])
    elif command == "delete" and len(args) >= 2:
        _cmd_delete(args[1])
    else:
        console.print()
        console.print(f"[red]Unknown command: {command}[/red]")
        console.print()
        console.print("Run [dim]python3 telegram_bot.py --help[/dim] for available commands")
        console.print()
        sys.exit(1)
