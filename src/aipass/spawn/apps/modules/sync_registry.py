# =================== META ====================
# Name: sync_registry.py
# Description: Registry repair — thin CLI layer for registry synchronization
# Version: 1.1.0
# Created: 2026-03-07
# Modified: 2026-03-07
# =============================================

"""Registry synchronization for branch lifecycle management.

Thin CLI module that parses arguments and delegates to the sync handler.
All implementation logic lives in apps/handlers/sync_registry_ops.py.
"""

from aipass.prax import logger
# CLI service: from cli.apps.modules import console (via aipass namespace)
from aipass.cli.apps.modules import console

from aipass.spawn.apps.handlers.sync_registry_ops import sync_registry


# =============================================================================
# PUBLIC API
# =============================================================================

def handle_sync_registry(args: list[str]) -> int:
    """Parse args and execute sync.

    Args patterns:
        []           -> report only (show mismatches)
        ["--fix"]    -> auto-repair mismatches

    Returns exit code (0=success, 1=failure).
    """
    if args and args[0] in ["--help", "-h"]:
        console.print("[yellow]Usage: drone @spawn sync-registry [--fix][/yellow]")
        console.print()
        console.print("  [green](no args)[/green]  Report mismatches between registry and filesystem")
        console.print("  [green]--fix[/green]      Auto-repair: remove stale, add unregistered")
        return 0

    fix = "--fix" in args

    try:
        result = sync_registry(fix=fix)
    except Exception as exc:
        logger.error(f"[sync-registry] Unexpected error: {exc}")
        console.print(f"[red]Error: {exc}[/red]")
        return 1

    _print_summary(result)
    return 0


# =============================================================================
# OUTPUT HELPERS
# =============================================================================

def _print_summary(result: dict) -> None:
    """Print a rich summary of the sync operation."""
    stale = result.get("stale", [])
    unregistered = result.get("unregistered", [])
    healthy = result.get("healthy", [])
    fixed = result.get("fixed", False)

    console.print()
    console.print("[bold]Registry Sync Report[/bold]")
    console.print()

    # Healthy
    if healthy:
        console.print(f"  [green]Healthy ({len(healthy)}):[/green]")
        for name in sorted(healthy):
            console.print(f"    {name}")

    # Stale
    if stale:
        console.print(f"  [red]Stale ({len(stale)}):[/red] [dim]registered but missing/invalid[/dim]")
        for name in sorted(stale):
            console.print(f"    {name}")
    else:
        console.print("  [green]No stale entries[/green]")

    # Unregistered
    if unregistered:
        console.print(f"  [yellow]Unregistered ({len(unregistered)}):[/yellow] [dim]on disk but not in registry[/dim]")
        for name in sorted(unregistered):
            console.print(f"    {name}")
    else:
        console.print("  [green]No unregistered branches[/green]")

    # Fix status
    if fixed:
        console.print()
        console.print("  [green]Registry has been repaired.[/green]")
    elif stale or unregistered:
        console.print()
        console.print("  [dim]Run with --fix to auto-repair.[/dim]")

    console.print()
