# ===================AIPASS====================
# META DATA HEADER
# Name: comment_module.py - Comment orchestration module
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
Comment Orchestration Module

Thin router for comment and vote workflows. Delegates all implementation
to handlers/comments/comment_ops.py and renders the results.

Handles: comment, vote commands.
"""

import logging
from typing import List

try:
    from aipass.prax.apps.modules.logger import system_logger as logger
except ImportError:
    logger = logging.getLogger("commons.comment_module")

try:
    from aipass.cli.apps.modules import console
except ImportError:
    from rich.console import Console
    console = Console()

from commons.apps.handlers.comments.comment_ops import add_comment, vote_on_content
from commons.apps.handlers.identity.identity_ops import resolve_display_name


# =============================================================================
# COMMAND ROUTING
# =============================================================================

def handle_command(command: str, args: List[str]) -> bool:
    """
    Handle comment and vote commands.

    Args:
        command: Command name (comment, vote).
        args: Command arguments.

    Returns:
        True if command handled, False otherwise.
    """
    if command == "comment":
        return _handle_comment(args)
    elif command == "vote":
        return _handle_vote(args)

    return False


# =============================================================================
# DISPLAY HANDLERS
# =============================================================================

def _handle_comment(args: List[str]) -> bool:
    """Add a comment and display the result."""
    result = add_comment(args)

    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    parent_note = f" (reply to comment {result['parent_id']})" if result.get("parent_id") else ""
    console.print()
    console.print(f"[green]Comment added to post {result['post_id']}{parent_note}[/green]")
    console.print(f"  [dim]Comment ID:[/dim] {result['comment_id']}")
    console.print(f"  [dim]Author:[/dim] {resolve_display_name(result['author'])}")
    if result.get("mentions"):
        console.print(f"  [dim]Mentions:[/dim] {', '.join(f'@{m}' for m in result['mentions'])}")
    console.print()

    return True


def _handle_vote(args: List[str]) -> bool:
    """Vote on content and display the result."""
    result = vote_on_content(args)

    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    action_msg = {
        "voted": f"Voted {result['direction']}",
        "changed": f"Changed vote to {result['direction']}",
        "removed": "Vote removed",
    }.get(result["action"], result["action"])

    arrow = "^" if result["direction"] == "up" else "v"

    console.print()
    console.print(
        f"[green]{arrow} {action_msg} on {result['target_type']} "
        f"{result['target_id']}[/green] [dim](score: {result['new_score']})[/dim]"
    )
    console.print()

    return True
