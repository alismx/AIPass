# ===================AIPASS====================
# META DATA HEADER
# Name: reaction_module.py - Curation Orchestration Module
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
Curation Orchestration Module

Thin router for thread curation and engagement workflows.
Delegates all implementation to handlers/curation/curation_ops.py
and renders results with Rich.

Handles: react, unreact, reactions, pin, unpin, pinned, trending commands.
"""

import logging
from typing import List

try:
    from aipass.prax.apps.modules.logger import system_logger as logger
except ImportError:
    logger = logging.getLogger("commons.reaction_module")

try:
    from aipass.cli.apps.modules import console
except ImportError:
    from rich.console import Console
    console = Console()

from commons.apps.handlers.curation.curation_ops import (
    add_react,
    remove_react,
    show_reactions,
    pin_post_cmd,
    unpin_post_cmd,
    show_pinned,
    show_trending,
)
from commons.apps.handlers.curation.reaction_queries import (
    REACTION_EMOJI,
    VALID_REACTIONS,
)


# =============================================================================
# COMMAND ROUTING
# =============================================================================

HANDLED_COMMANDS = ["react", "unreact", "reactions", "pin", "unpin", "pinned", "trending"]


def handle_command(command: str, args: List[str]) -> bool:
    """
    Handle curation-related commands.

    Args:
        command: Command name
        args: Command arguments

    Returns:
        True if command handled, False otherwise
    """
    if command not in HANDLED_COMMANDS:
        return False

    if command == "react":
        return _handle_react(args)
    elif command == "unreact":
        return _handle_unreact(args)
    elif command == "reactions":
        return _handle_reactions(args)
    elif command == "pin":
        return _handle_pin(args)
    elif command == "unpin":
        return _handle_unpin(args)
    elif command == "pinned":
        return _handle_pinned(args)
    elif command == "trending":
        return _handle_trending(args)

    return False


# =============================================================================
# DISPLAY HANDLERS
# =============================================================================

def _handle_react(args: List[str]) -> bool:
    """Add a reaction and display result."""
    result = add_react(args)

    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    emoji = result["emoji"]
    if result["is_new"]:
        console.print()
        console.print(
            f"[green]{emoji} Reacted with {result['reaction']} on "
            f"{result['target_type']} {result['target_id']}[/green]"
        )
        console.print()
    else:
        console.print(
            f"[yellow]Already reacted with {result['reaction']} on "
            f"{result['target_type']} {result['target_id']}[/yellow]"
        )

    return True


def _handle_unreact(args: List[str]) -> bool:
    """Remove a reaction and display result."""
    result = remove_react(args)

    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    emoji = result["emoji"]
    if result["removed"]:
        console.print()
        console.print(
            f"[green]{emoji} Removed {result['reaction']} from "
            f"{result['target_type']} {result['target_id']}[/green]"
        )
        console.print()
    else:
        console.print(
            f"[yellow]No {result['reaction']} reaction found on "
            f"{result['target_type']} {result['target_id']}[/yellow]"
        )

    return True


def _handle_reactions(args: List[str]) -> bool:
    """Show reactions on a target."""
    result = show_reactions(args)

    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    detailed = result["reactions"]

    console.print()
    if not detailed:
        console.print(f"[dim]No reactions on {result['target_type']} #{result['target_id']}[/dim]")
    else:
        console.print(f"[bold]Reactions on {result['target_type']} #{result['target_id']}:[/bold]")
        for reaction_type in VALID_REACTIONS:
            if reaction_type in detailed:
                agents = detailed[reaction_type]
                emoji = REACTION_EMOJI[reaction_type]
                agents_str = ", ".join(agents)
                console.print(f"  {emoji} {len(agents)} ({agents_str})")
    console.print()

    return True


def _handle_pin(args: List[str]) -> bool:
    """Pin a post and display result."""
    result = pin_post_cmd(args)

    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    console.print()
    console.print(f'[green]Pinned post #{result["post_id"]} "{result["title"]}"[/green]')
    console.print()

    return True


def _handle_unpin(args: List[str]) -> bool:
    """Unpin a post and display result."""
    result = unpin_post_cmd(args)

    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    console.print()
    console.print(f'[green]Unpinned post #{result["post_id"]} "{result["title"]}"[/green]')
    console.print()

    return True


def _handle_pinned(args: List[str]) -> bool:
    """Show pinned posts."""
    result = show_pinned(args)

    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    posts = result["posts"]
    room_name = result.get("room")

    console.print()
    if not posts:
        if room_name:
            console.print(f"[dim]No pinned posts in r/{room_name}[/dim]")
        else:
            console.print("[dim]No pinned posts[/dim]")
    else:
        console.print("[bold]Pinned Posts:[/bold]")
        for post in posts:
            score_str = f"+{post['vote_score']}" if post["vote_score"] >= 0 else str(post["vote_score"])
            console.print(
                f'  [cyan]PIN[/cyan] #{post["id"]} "{post["title"]}" '
                f'by {post["author"]} in r/{post["room_name"]} [{score_str}]'
            )
    console.print()

    return True


def _handle_trending(args: List[str]) -> bool:
    """Show trending posts."""
    result = show_trending(args)

    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    posts = result["posts"]

    console.print()
    if not posts:
        console.print("[dim]Nothing trending right now[/dim]")
    else:
        console.print("[bold]Trending Now:[/bold]")
        for post in posts:
            console.print(
                f'  [bold red]TREND[/bold red] #{post["id"]} "{post["title"]}" '
                f'by {post["author"]} in r/{post["room_name"]}'
            )
            console.print(
                f'     {post["engagement_count"]} engagements '
                f'({post["vote_count"]} votes, {post["comment_count"]} comments, '
                f'{post["reaction_count"]} reactions)'
            )
    console.print()

    return True
