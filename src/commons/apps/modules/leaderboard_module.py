# ===================AIPASS====================
# META DATA HEADER
# Name: leaderboard_module.py - Leaderboard Module
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
Leaderboard Module

Thin router for leaderboard commands. Delegates all query logic
to handlers/social/leaderboard_ops.py and renders results as Rich tables.

Handles: leaderboard, leaderboards commands.
"""

import logging
from typing import List

try:
    from aipass.prax.apps.modules.logger import system_logger as logger
except ImportError:
    logger = logging.getLogger("commons.leaderboard_module")

try:
    from aipass.cli.apps.modules import console
except ImportError:
    from rich.console import Console
    console = Console()

from rich.table import Table

from commons.apps.handlers.social.leaderboard_ops import show_leaderboard, VALID_CATEGORIES


# =============================================================================
# COMMAND ROUTING
# =============================================================================

def handle_command(command: str, args: List[str]) -> bool:
    """
    Handle leaderboard commands.

    Args:
        command: Command name (leaderboard, leaderboards)
        args: Command arguments

    Returns:
        True if command handled, False otherwise
    """
    if command not in ("leaderboard", "leaderboards"):
        return False

    return _handle_leaderboard(args)


# =============================================================================
# DISPLAY HANDLER
# =============================================================================

BOARD_TITLES = {
    "artifacts": "Most Artifacts",
    "trades": "Most Trades",
    "posts": "Most Posts",
    "rooms": "Most Active Rooms (7 days)",
    "karma": "Top Karma",
}

BOARD_COLUMNS = {
    "artifacts": ("Branch", "Artifacts"),
    "trades": ("Branch", "Trades/Gifts"),
    "posts": ("Branch", "Posts"),
    "rooms": ("Room", "Posts (7d)"),
    "karma": ("Branch", "Karma"),
}


def _handle_leaderboard(args: List[str]) -> bool:
    """Query leaderboard data and render as Rich tables."""
    result = show_leaderboard(args)

    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    boards = result["boards"]

    console.print()
    console.print("[bold cyan]--- Leaderboards ---[/bold cyan]")
    console.print()

    for category in VALID_CATEGORIES:
        if category not in boards:
            continue

        rows = boards[category]
        title = BOARD_TITLES[category]
        name_col, count_col = BOARD_COLUMNS[category]

        if not rows:
            console.print(f"[dim]No data for {title.lower()}.[/dim]")
            console.print()
            continue

        table = Table(title=title, border_style="cyan")
        table.add_column("Rank", style="dim", width=5)
        table.add_column(name_col, style="bold")
        table.add_column(count_col, justify="right")

        for i, row in enumerate(rows, 1):
            if category == "rooms":
                name = f"r/{row['room']}"
            else:
                name = row["branch"]
            table.add_row(str(i), name, str(row["count"]))

        console.print(table)
        console.print()

    return True
