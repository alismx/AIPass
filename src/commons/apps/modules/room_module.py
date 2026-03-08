# ===================AIPASS====================
# META DATA HEADER
# Name: room_module.py - Room management orchestration module
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
Room Management Module

Thin router for room management. Delegates all implementation
to handlers/rooms/room_ops.py and renders the results.

Handles: room create, room list, room join commands.
"""

import logging
from typing import List

try:
    from aipass.prax.apps.modules.logger import system_logger as logger
except ImportError:
    logger = logging.getLogger("commons.room_module")

try:
    from aipass.cli.apps.modules import console
except ImportError:
    from rich.console import Console
    console = Console()

from rich.table import Table

from commons.apps.handlers.rooms.room_ops import create_room, list_rooms, join_room


# =============================================================================
# COMMAND ROUTING
# =============================================================================

def handle_command(command: str, args: List[str]) -> bool:
    """
    Handle room-related commands.

    Args:
        command: Command name (room).
        args: Command arguments (subcommand + params).

    Returns:
        True if command handled, False otherwise.
    """
    if command != "room":
        return False

    if not args:
        return _handle_list_rooms([])

    subcommand = args[0].lower()
    sub_args = args[1:]

    if subcommand == "create":
        return _handle_create_room(sub_args)
    elif subcommand == "list":
        return _handle_list_rooms(sub_args)
    elif subcommand == "join":
        return _handle_join_room(sub_args)
    else:
        console.print(f"[red]Unknown room subcommand: {subcommand}[/red]")
        console.print("[dim]Available: create, list, join[/dim]")
        return True


# =============================================================================
# DISPLAY HANDLERS
# =============================================================================

def _handle_create_room(args: List[str]) -> bool:
    """Create a room and display the result."""
    result = create_room(args)

    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    console.print()
    console.print(f"[green]Room '{result['name']}' created![/green]")
    if result.get("description"):
        console.print(f"  [dim]Description:[/dim] {result['description']}")
    console.print(f"  [dim]Created by:[/dim] {result['created_by']}")
    console.print()

    return True


def _handle_list_rooms(args: List[str]) -> bool:
    """List rooms and display as a Rich table."""
    result = list_rooms(args)

    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    rooms = result["rooms"]

    console.print()
    console.print(f"[bold cyan]Rooms in The Commons[/bold cyan] [dim]({len(rooms)} rooms)[/dim]")
    console.print()

    if not rooms:
        console.print("[dim]  No rooms yet. Create one with: room create <name> [description][/dim]")
        console.print()
        return True

    table = Table(show_header=True, header_style="bold", expand=False, padding=(0, 1))
    table.add_column("Room", style="cyan", min_width=15)
    table.add_column("Description", min_width=30)
    table.add_column("Members", width=8, justify="center")
    table.add_column("Posts", width=8, justify="center")

    for room in rooms:
        table.add_row(
            room["name"],
            room.get("description", "") or "[dim]--[/dim]",
            str(room.get("member_count", 0)),
            str(room.get("post_count", 0)),
        )

    console.print(table)
    console.print()

    return True


def _handle_join_room(args: List[str]) -> bool:
    """Join a room and display the result."""
    result = join_room(args)

    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    console.print()
    console.print(f"[green]{result['agent']} joined room '{result['room']}'![/green]")
    console.print()

    return True
