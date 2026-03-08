# ===================AIPASS====================
# META DATA HEADER
# Name: engagement_module.py - Engagement Orchestration Module
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
Engagement Orchestration Module

Thin router for community engagement workflows. Delegates all
implementation to handlers/engagement/engagement_ops.py and
renders results with Rich.

Handles: prompt, event commands.
"""

import logging
from typing import List

try:
    from aipass.prax.apps.modules.logger import system_logger as logger
except ImportError:
    logger = logging.getLogger("commons.engagement_module")

try:
    from aipass.cli.apps.modules import console
except ImportError:
    from rich.console import Console
    console = Console()

from commons.apps.handlers.engagement.engagement_ops import generate_prompt, create_event


# =============================================================================
# COMMAND ROUTING
# =============================================================================

HANDLED_COMMANDS = ["prompt", "event"]


def handle_command(command: str, args: List[str]) -> bool:
    """
    Handle engagement-related commands.

    Args:
        command: Command name (prompt, event)
        args: Command arguments

    Returns:
        True if command handled, False otherwise
    """
    if command not in HANDLED_COMMANDS:
        return False

    if command == "prompt":
        return _handle_prompt(args)
    elif command == "event":
        return _handle_event(args)

    return False


# =============================================================================
# DISPLAY HANDLERS
# =============================================================================

def _handle_prompt(args: List[str]) -> bool:
    """Generate a daily prompt and display result."""
    result = generate_prompt(args)

    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    console.print()
    console.print("[green]Daily prompt posted![/green]")
    console.print(f"  [dim]ID:[/dim] {result['post_id']}")
    console.print(f"  [dim]Room:[/dim] r/{result['room']}")
    console.print(f"  [dim]Theme:[/dim] {result['theme']}")
    console.print(f"  [dim]Author:[/dim] {result['author']}")
    console.print()

    return True


def _handle_event(args: List[str]) -> bool:
    """Create an event and display result."""
    result = create_event(args)

    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    console.print()
    console.print("[green]Event created![/green]")
    console.print(f"  [dim]ID:[/dim] {result['post_id']}")
    console.print(f"  [dim]Room:[/dim] r/{result['room']}")
    console.print(f"  [dim]Title:[/dim] {result['title']}")
    console.print(f"  [dim]Type:[/dim] announcement")
    console.print(f"  [dim]Author:[/dim] {result['author']}")
    console.print()

    return True
