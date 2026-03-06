
# ===================AIPASS====================
# META DATA HEADER
# Name: run_module.py - PRAX Run Command
# Date: 2025-11-15
# Version: 1.0.0
# Category: prax/modules
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2025-11-15): Created with handle_command interface
#
# CODE STANDARDS:
#   - Follows AIPass Prax standards
#   - Implements handle_command(command: str, args: List[str]) -> bool interface
#   - Uses Prax logger for system-wide logging
# =============================================

"""
PRAX Run Module

Implements the 'run' command using handle_command interface.
"""

import sys
from pathlib import Path
from typing import List

from aipass.prax.apps.modules.logger import start_continuous_logging, system_logger as logger
from aipass.cli.apps.modules import console, header, success, error


def print_help():
    """Display module help and connected handlers"""
    console.print()
    console.print("[bold cyan]PRAX Run Module[/bold cyan]")
    console.print()
    console.print("[yellow]Connected Handlers:[/yellow]")
    console.print()

    console.print("  [cyan]prax/modules/[/cyan]")
    console.print("    [dim]- logger.py[/dim] (start_continuous_logging, system_logger)")
    console.print()

    console.print("[dim]Run 'python3 run_module.py --help' for usage[/dim]")
    console.print()


def handle_command(command: str, args: List[str]) -> bool:
    """
    Handle run command

    Args:
        command: Command name
        args: Command arguments

    Returns:
        True if command was handled
    """
    if command != 'run':
        return False

    console.print("🚀 Starting PRAX continuous logging mode...")
    start_continuous_logging()
    return True


if __name__ == "__main__":
    # Show introspection when run without arguments
    if len(sys.argv) == 1:
        print_help()
        sys.exit(0)
