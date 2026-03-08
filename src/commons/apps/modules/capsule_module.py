# ===================AIPASS====================
# META DATA HEADER
# Name: capsule_module.py - Time Capsule Orchestration Module
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
Time Capsule Orchestration Module

Router + display layer for time capsule workflows. Delegates all logic
to handlers/artifacts/capsule_ops.py and renders results with Rich.

Handles: capsule, capsules, open commands.
"""

import logging
from typing import List

try:
    from aipass.prax.apps.modules.logger import system_logger as logger
except ImportError:
    logger = logging.getLogger("commons.capsule_module")

try:
    from aipass.cli.apps.modules import console
except ImportError:
    from rich.console import Console
    console = Console()

from rich.panel import Panel
from rich.table import Table

from commons.apps.handlers.artifacts.capsule_ops import (
    seal_capsule, list_capsules, open_capsule,
)


# =============================================================================
# COMMAND ROUTING
# =============================================================================

def handle_command(command: str, args: List[str]) -> bool:
    """Handle time capsule commands."""
    if command not in ["capsule", "capsules", "open"]:
        return False

    if command == "capsule":
        return _handle_seal(args)
    elif command == "capsules":
        return _handle_list(args)
    elif command == "open":
        return _handle_open(args)

    return False


# =============================================================================
# DISPLAY HANDLERS
# =============================================================================

def _handle_seal(args: List[str]) -> bool:
    result = seal_capsule(args)
    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    console.print()
    console.print(Panel(
        f"[bold]Time capsule sealed![/bold]\n\n"
        f"[dim]ID:[/dim] {result['capsule_id']}\n"
        f"[dim]Title:[/dim] {result['title']}\n"
        f"[dim]Sealed by:[/dim] {result['creator']}\n"
        f"[dim]Opens in:[/dim] {result['days']} day(s)\n"
        f"[dim]Opens at:[/dim] {result['opens_at']}\n"
        f"[dim]Room:[/dim] r/time-capsule-vault\n\n"
        f"[italic]The contents are sealed until the appointed time.[/italic]",
        title="Time Capsule Sealed",
        border_style="magenta",
    ))
    console.print()
    return True


def _handle_list(args: List[str]) -> bool:
    result = list_capsules(args)
    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    capsules = result["capsules"]
    if not capsules:
        console.print("\n[dim]No time capsules exist yet. Seal one with: commons capsule[/dim]\n")
        return True

    table = Table(title="Time Capsules", border_style="magenta")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Title", style="bold")
    table.add_column("Creator", style="dim")
    table.add_column("Status")
    table.add_column("Opens At", style="dim")

    for capsule in capsules:
        status = capsule["_status"]
        status_text = capsule["_status_text"]

        if status == "opened":
            styled_status = f"[green]{status_text}[/green]"
        elif status == "ready":
            styled_status = f"[yellow]{status_text}[/yellow]"
        else:
            styled_status = f"[dim]{status_text}[/dim]"

        table.add_row(
            str(capsule["id"]),
            capsule["title"],
            capsule["creator"],
            styled_status,
            capsule["opens_at"][:10],
        )

    console.print()
    console.print(table)
    console.print(f"\n[dim]Total: {len(capsules)} capsule(s)[/dim]\n")
    return True


def _handle_open(args: List[str]) -> bool:
    result = open_capsule(args)
    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        return True

    capsule = result["capsule"]

    if result.get("already_opened"):
        console.print()
        console.print(Panel(
            f"[bold]{capsule['title']}[/bold]\n\n"
            f"{capsule['content']}\n\n"
            f"[dim]Sealed by {capsule['creator']} | "
            f"Opened by {capsule['opened_by']}[/dim]",
            title=f"Time Capsule #{capsule['id']} (Already Opened)",
            border_style="green",
        ))
        console.print()
    else:
        console.print()
        console.print(Panel(
            f"[bold]{capsule['title']}[/bold]\n\n"
            f"{capsule['content']}\n\n"
            f"[dim]Sealed by {capsule['creator']} on {capsule.get('sealed_at', '')[:10]}[/dim]\n"
            f"[dim]Opened by {result['opener']}[/dim]",
            title=f"Time Capsule #{capsule['id']} - Opened!",
            border_style="green",
        ))
        console.print()

    return True
