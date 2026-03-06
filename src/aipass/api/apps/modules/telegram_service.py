
# ===================AIPASS====================
# META DATA HEADER
# Name: telegram_service.py - Telegram Service Control Module
# Date: 2026-02-03
# Version: 1.0.0
# Category: api/modules
# CODE STANDARDS: Seed v1.0.0
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-02-03): Initial module - systemd service control for telegram bridge
# =============================================

"""
Telegram Service Control Module

Manages the telegram-bridge systemd user service:
- drone @api telegram start  → Start service
- drone @api telegram stop   → Stop service
- drone @api telegram status → Check service status
"""

import sys
from pathlib import Path

from typing import List
from aipass.prax.apps.modules.logger import system_logger as logger
from aipass.cli.apps.modules import console, header, success, error, warning
from aipass.api.apps.handlers.telegram_service import service


def print_introspection() -> None:
    """Show module introspection"""
    console.print()
    header("Telegram Service Control Introspection")
    console.print()

    console.print("[cyan]Purpose:[/cyan] Manage telegram-bridge systemd service")
    console.print()

    console.print("[cyan]Connected Handlers:[/cyan]")
    console.print("  • api.apps.handlers.telegram_service.service")
    console.print()

    console.print("[cyan]Available Commands:[/cyan]")
    console.print("  • telegram start  - Start the service")
    console.print("  • telegram stop   - Stop the service")
    console.print("  • telegram status - Check service status")
    console.print("  • telegram logs   - View recent logs")
    console.print()

    console.print("[cyan]Service:[/cyan]")
    console.print(f"  • Name: {service.SERVICE_NAME}.service")
    console.print("  • Type: systemd user service")
    console.print()


def print_help() -> None:
    """Print module help"""
    import argparse

    parser = argparse.ArgumentParser(
        prog="drone @api telegram",
        description="Telegram Service Control - Manage the telegram-bridge service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
SUBCOMMANDS:
  start            - Start the telegram-bridge service
  stop             - Stop the telegram-bridge service
  status           - Check service status
  logs             - View recent service logs

USAGE:
  drone @api telegram start
  drone @api telegram stop
  drone @api telegram status
  drone @api telegram logs

EXAMPLES:
  # Start the bot
  drone @api telegram start

  # Check if running
  drone @api telegram status

  # Stop the bot
  drone @api telegram stop

  # View logs
  drone @api telegram logs
        """
    )
    console.print(parser.format_help())


def handle_command(command: str, args: List[str]) -> bool:
    """
    Handle telegram service commands

    Args:
        command: Command name (should be 'telegram')
        args: Subcommand and arguments

    Returns:
        True if command was handled, False otherwise
    """
    if command != "telegram":
        return False

    try:
        if not args:
            print_help()
            return True

        subcommand = args[0]

        if subcommand == "start":
            _handle_start()
        elif subcommand == "stop":
            _handle_stop()
        elif subcommand == "status":
            _handle_status()
        elif subcommand == "logs":
            _handle_logs()
        elif subcommand in ["--help", "-h", "help"]:
            print_help()
        else:
            error(f"Unknown subcommand: {subcommand}")
            console.print()
            console.print("[dim]Use 'drone @api telegram --help' for usage[/dim]")

        return True
    except Exception as e:
        logger.error("Error in telegram_service.handle_command: %s", str(e))
        raise


def _handle_start() -> None:
    """Orchestrate service start"""
    header("Telegram Bridge Service")
    console.print()

    ok, msg = service.start_service()

    if ok:
        success(msg)
        console.print()
        console.print("[dim]Check status: drone @api telegram status[/dim]")
        console.print("[dim]View logs: drone @api telegram logs[/dim]")
    else:
        error(f"Failed to start service: {msg}")


def _handle_stop() -> None:
    """Orchestrate service stop"""
    header("Telegram Bridge Service")
    console.print()

    ok, msg = service.stop_service()

    if ok:
        success(msg)
    else:
        error(f"Failed to stop service: {msg}")


def _handle_status() -> None:
    """Orchestrate status check"""
    header("Telegram Bridge Service Status")
    console.print()

    status_code, output = service.get_status()

    if status_code == "running":
        success("Service is running")
    elif status_code == "stopped":
        warning("Service is stopped")
    elif status_code == "not_found":
        error("Service not found - run 'systemctl --user daemon-reload'")
    else:
        warning("Unknown status")

    console.print()

    for line in output.split("\n"):
        line = line.strip()
        if any(k in line for k in ["Active:", "Main PID:", "Memory:", "CPU:"]):
            console.print(f"  {line}")

    console.print()
    console.print("[dim]Logs: drone @api telegram logs[/dim]")


def _handle_logs() -> None:
    """Orchestrate log retrieval"""
    header("Telegram Bridge Service Logs")
    console.print()

    ok, content = service.get_logs(30)

    if not ok:
        warning(content)
        return

    console.print(f"[dim]Showing last 30 lines[/dim]")
    console.print()

    for line in content.split("\n"):
        console.print(line.rstrip())


if __name__ == "__main__":
    """Standalone execution mode"""
    args = sys.argv[1:]

    if len(args) == 0:
        print_introspection()
        sys.exit(0)

    if args[0] in ['--help', '-h', 'help']:
        print_help()
        sys.exit(0)

    if handle_command("telegram", args):
        sys.exit(0)
    else:
        console.print()
        console.print(f"[red]Unknown command: {args[0]}[/red]")
        console.print()
        sys.exit(1)
