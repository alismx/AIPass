# ===================AIPASS====================
# META DATA HEADER
# Name: welcome_module.py - Welcome Orchestration Module
# Date: 2026-03-07
# Version: 1.0.0
# Category: commons/apps/modules
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-03-07): Ported from dev system (FPLAN-0411)
#
# CODE STANDARDS:
#   - Orchestration only - NO business logic
#   - Imports from handlers/ for all data operations
#   - Module interface: handle_command(command, args) -> bool
#   - No sys.path manipulation
# =============================================

"""
Welcome & Onboarding Orchestration Module

Thin router for the welcome command. Delegates logic
to handlers/welcome/welcome_ops.py and renders results with Rich.

Handles: welcome command.
"""

import logging
from typing import List

try:
    from aipass.prax.apps.modules.logger import system_logger as logger
except ImportError:
    logger = logging.getLogger("commons.welcome_module")

try:
    from aipass.cli.apps.modules import console
except ImportError:
    from rich.console import Console
    console = Console()

from commons.apps.handlers.welcome.welcome_ops import run_welcome


# =============================================================================
# COMMAND ROUTING
# =============================================================================

def handle_command(command: str, args: List[str]) -> bool:
    """
    Handle welcome-related commands.

    Args:
        command: Command name (welcome)
        args: Command arguments

    Returns:
        True if command handled, False otherwise
    """
    if command != "welcome":
        return False

    return _handle_welcome(args)


# =============================================================================
# DISPLAY HANDLER
# =============================================================================

def _handle_welcome(args: List[str]) -> bool:
    """Run welcome and display results."""
    result = run_welcome(args)

    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    console.print()

    if result["action"] == "scan":
        welcomed = result["welcomed"]
        console.print("[bold cyan]Checking for new branches to welcome...[/bold cyan]")
        console.print()

        if welcomed:
            for name in welcomed:
                console.print(f"  Welcome post created for: [green]@{name}[/green]")
            console.print()
            console.print(f"[bold]{len(welcomed)} new branch(es) welcomed![/bold]")
        else:
            console.print("  [dim]All branches have been welcomed already.[/dim]")

    elif result["action"] == "specific":
        branch = result["branch"]
        if result.get("already_welcomed"):
            console.print(f"  [dim]@{branch} has already been welcomed.[/dim]")
        else:
            console.print(f"  Welcome post created for: [green]@{branch}[/green]")

    console.print()

    return True
