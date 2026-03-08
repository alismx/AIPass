# ===================AIPASS====================
# META DATA HEADER
# Name: digest_module.py - Digest Orchestration Module
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
Digest Orchestration Module

Thin router for community digest workflows. Delegates query logic
to handlers/digest/digest_ops.py and renders results with Rich.

Handles: digest command.
"""

import logging
from typing import List

try:
    from aipass.prax.apps.modules.logger import system_logger as logger
except ImportError:
    logger = logging.getLogger("commons.digest_module")

try:
    from aipass.cli.apps.modules import console
except ImportError:
    from rich.console import Console
    console = Console()

from rich.panel import Panel

from commons.apps.handlers.digest.digest_ops import show_digest


# =============================================================================
# COMMAND ROUTING
# =============================================================================

def handle_command(command: str, args: List[str]) -> bool:
    """
    Handle digest-related commands.

    Args:
        command: Command name (digest)
        args: Command arguments

    Returns:
        True if command handled, False otherwise
    """
    if command != "digest":
        return False

    return _handle_digest(args)


# =============================================================================
# DISPLAY HANDLER
# =============================================================================

def _handle_digest(args: List[str]) -> bool:
    """Query digest and display results."""
    result = show_digest(args)

    if not result["success"]:
        console.print(f"[red]Failed to generate digest: {result['error']}[/red]")
        return True

    top_posts = result["top_posts"]
    active_branches = result["active_branches"]
    new_branches = result["new_branches"]
    totals = result["totals"]

    console.print()

    # Header
    console.print(Panel(
        "[bold]Community Activity Digest[/bold]\n"
        "[dim]Last 24 hours[/dim]",
        border_style="cyan",
        expand=False,
    ))
    console.print()

    # Activity totals
    console.print(
        f"  [bold cyan]Activity:[/bold cyan] "
        f"{totals['total_posts']} posts, "
        f"{totals['total_comments']} comments"
    )
    console.print()

    # Top posts
    if top_posts:
        console.print("[bold cyan]Top Posts by Engagement:[/bold cyan]")
        console.print()
        for i, post in enumerate(top_posts, 1):
            engagement = post["engagement_count"]
            console.print(
                f"  [bold]{i}.[/bold] "
                f'[yellow]#{post["id"]}[/yellow] "{post["title"]}" '
                f'by [green]{post["author"]}[/green] in r/{post["room_name"]}'
            )
            console.print(
                f"     {engagement} engagements "
                f'({post["vote_count"]} votes, '
                f'{post["comment_count"]} comments, '
                f'{post["reaction_count"]} reactions)'
            )
        console.print()
    else:
        console.print("[dim]  No posts with engagement in the last 24h[/dim]")
        console.print()

    # Most active branches
    if active_branches:
        console.print("[bold cyan]Most Active Branches:[/bold cyan]")
        console.print()
        for branch in active_branches:
            console.print(
                f"  [green]{branch['agent']}[/green] - "
                f"{branch['total_activity']} actions "
                f"({branch['post_count']} posts, {branch['comment_count']} comments)"
            )
        console.print()
    else:
        console.print("[dim]  No branch activity in the last 24h[/dim]")
        console.print()

    # New branches
    if new_branches:
        console.print("[bold cyan]New Branches:[/bold cyan]")
        console.print()
        for name in new_branches:
            console.print(f"  [green]+[/green] {name}")
        console.print()
    else:
        console.print("[dim]  No new branches in the last 24h[/dim]")
        console.print()

    return True
