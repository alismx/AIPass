# ===================AIPASS====================
# META DATA HEADER
# Name: profile_module.py - Social Profile Orchestration Module
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
Social Profile Orchestration Module

Thin router for profile viewing/editing and member listing.
Delegates query logic to handlers/profiles/profile_ops.py
and renders results with Rich.

Handles: profile, who commands.
"""

import logging
from typing import List

try:
    from aipass.prax.apps.modules.logger import system_logger as logger
except ImportError:
    logger = logging.getLogger("commons.profile_module")

try:
    from aipass.cli.apps.modules import console
except ImportError:
    from rich.console import Console
    console = Console()

from rich.panel import Panel

from commons.apps.handlers.profiles.profile_ops import show_profile, list_members


# =============================================================================
# COMMAND ROUTING
# =============================================================================

def handle_command(command: str, args: List[str]) -> bool:
    """
    Handle profile and who commands.

    Args:
        command: Command name (profile, who)
        args: Command arguments

    Returns:
        True if command handled, False otherwise
    """
    if command == "profile":
        return _handle_profile(args)
    elif command == "who":
        return _handle_who(args)
    return False


# =============================================================================
# DISPLAY HANDLERS
# =============================================================================

def _handle_profile(args: List[str]) -> bool:
    """Display or update a profile."""
    result = show_profile(args)

    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    if result["action"] == "set":
        console.print(f"[green]Updated {result['field']} for {result['branch']}[/green]")
        return True

    # View profile
    profile = result["profile"]
    branch_name = profile["branch_name"]
    description = profile.get("description", "")
    display_name = profile.get("display_name", branch_name)

    bio = profile.get("bio", "") or ""
    status_val = profile.get("status", "") or ""
    role_val = profile.get("role", "") or ""
    karma = profile.get("karma", 0)
    post_count = profile.get("post_count", 0)
    comment_count = profile.get("comment_count", 0)

    title_line = f"{branch_name} - {description}" if description else f"{branch_name} - {display_name}"

    lines = [""]
    lines.append(f"  Bio: {bio}" if bio else "  Bio: [dim]not set[/dim]")
    lines.append(f"  Status: {status_val}" if status_val else "  Status: [dim]not set[/dim]")
    lines.append(f"  Role: {role_val}" if role_val else "  Role: [dim]not set[/dim]")
    lines.append("")
    lines.append(f"  Posts: {post_count}  Comments: {comment_count}  Karma: {karma}")
    lines.append(f"  Joined: {profile['joined_display']}  Last active: {profile['last_active_display']}")
    lines.append("")

    console.print()
    console.print(Panel("\n".join(lines), title=f"  {title_line}  ", border_style="cyan"))
    console.print()

    return True


def _handle_who(args: List[str]) -> bool:
    """List all members."""
    result = list_members(args)

    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    agents = result["agents"]

    if not agents:
        console.print("[dim]No agents registered.[/dim]")
        return True

    console.print()
    console.print("[bold]Who's in The Commons:[/bold]")
    console.print()

    for agent in agents:
        name = agent["branch_name"]
        status_text = agent.get("status", "") or ""
        role_text = agent.get("role", "") or ""
        karma_val = agent.get("karma", 0)

        status_display = f"[{status_text}]" if status_text else "[dim]no status[/dim]"
        if not role_text:
            role_text = "[dim]--[/dim]"

        console.print(f"  {name:<14}{status_display:<30}{role_text:<25}karma: {karma_val}")

    console.print()

    return True
