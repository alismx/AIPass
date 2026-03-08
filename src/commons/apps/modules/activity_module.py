# ===================AIPASS====================
# META DATA HEADER
# Name: activity_module.py - Activity Feed Orchestration Module
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
Activity Feed Orchestration Module

Thin router for the activity command. Delegates query logic
to handlers/activity/activity_ops.py and renders results with Rich.

Handles: activity command.
"""

import logging
from typing import List

try:
    from aipass.prax.apps.modules.logger import system_logger as logger
except ImportError:
    logger = logging.getLogger("commons.activity_module")

try:
    from aipass.cli.apps.modules import console
except ImportError:
    from rich.console import Console
    console = Console()

from rich.table import Table

from commons.apps.handlers.activity.activity_ops import run_activity
from commons.apps.handlers.identity.identity_ops import resolve_display_name


# =============================================================================
# COMMAND ROUTING
# =============================================================================

def handle_command(command: str, args: List[str]) -> bool:
    """
    Handle activity-related commands.

    Args:
        command: Command name (activity)
        args: Command arguments

    Returns:
        True if command handled, False otherwise
    """
    if command != "activity":
        return False

    return _handle_activity(args)


# =============================================================================
# DISPLAY HANDLER
# =============================================================================

def _handle_activity(args: List[str]) -> bool:
    """Query activity and display as Rich table."""
    result = run_activity(args)

    if not result["success"]:
        if result.get("error"):
            console.print(f"[red]{result['error']}[/red]")
        return True

    if result.get("help"):
        console.print(result["help_text"])
        return True

    activities = result["activities"]
    room_filter = result.get("room_filter")

    console.print()

    if not activities:
        if room_filter:
            console.print(f"[dim]No recent activity in room '{room_filter}'.[/dim]")
        else:
            console.print("[dim]No recent activity in The Commons.[/dim]")
        console.print()
        return True

    title = "Recent Activity"
    if room_filter:
        title += f" in #{room_filter}"

    table = Table(title=title, show_lines=False, pad_edge=True)
    table.add_column("Time", style="dim", no_wrap=True, width=10)
    table.add_column("Author", style="cyan", no_wrap=True, width=14)
    table.add_column("Thread", style="green", no_wrap=True, width=30)
    table.add_column("Comment", style="white", width=60)

    for activity in activities:
        author = resolve_display_name(activity["author"])
        table.add_row(
            activity["time"],
            author,
            activity["title"],
            activity["content"],
        )

    console.print(table)
    console.print()

    return True
