
# ===================AIPASS====================
# META DATA HEADER
# Name: discover_module.py - PRAX Discover Command
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
PRAX Discover Module

Implements the 'discover' command using handle_command interface.
"""

import sys
from typing import List

from aipass.prax.apps.modules.logger import system_logger as logger
from aipass.cli.apps.modules import console, header, success, error
from aipass.prax.apps.handlers.discovery.scanner import discover_python_modules


def print_help():
    """Display module help and connected handlers"""
    console.print()
    console.print("[bold cyan]PRAX Discover Module[/bold cyan]")
    console.print()
    console.print("[yellow]Connected Handlers:[/yellow]")
    console.print()

    console.print("  [cyan]prax/modules/[/cyan]")
    console.print("    [dim]- logger.py[/dim] (system_logger)")
    console.print()

    console.print("  [cyan]prax/handlers/discovery/[/cyan]")
    console.print("    [dim]- scanner.py[/dim] (discover_python_modules)")
    console.print()

    console.print("[dim]Run 'python3 discover_module.py --help' for usage[/dim]")
    console.print()


def handle_command(command: str, args: List[str]) -> bool:
    """
    Handle discover command

    Args:
        command: Command name
        args: Command arguments

    Returns:
        True if command was handled
    """
    if command != 'discover':
        return False

    console.print("🔍 Discovering Python modules...")
    modules = discover_python_modules()
    console.print(f"✅ Discovered {len(modules)} modules")
    return True


if __name__ == "__main__":
    # Show introspection when run without arguments
    if len(sys.argv) == 1:
        print_help()
        sys.exit(0)
