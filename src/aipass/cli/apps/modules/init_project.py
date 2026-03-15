# =================== AIPass ====================
# Name: init_project.py
# Description: Init Project Module — orchestration layer for aipass init
# Version: 1.0.0
# Created: 2026-03-14
# Modified: 2026-03-14
# =============================================

"""
Init Project Module - PUBLIC API

Thin orchestration module for the `aipass init` command.
Routes to the init bootstrap handler for business logic.

Usage:
    drone @cli aipass init [target_dir] [project_name]
"""

import os
import sys
from pathlib import Path
from typing import List

from aipass.cli.apps.handlers.init.bootstrap import init_project
from aipass.cli.apps.modules.display import console, success, error, header


# =============================================================================
# MODULE PATTERN FUNCTIONS (SEED compliant)
# =============================================================================

def print_introspection():
    """Display module info and connected handlers."""
    console.print()
    console.print("[bold cyan]Init Project Module[/bold cyan]")
    console.print()
    console.print("[dim]Bootstrap an AIPass project in any directory[/dim]")
    console.print()

    console.print("[yellow]Connected Handlers:[/yellow]")
    console.print()
    console.print("  [cyan]handlers/init/[/cyan]")
    console.print("    [dim]- bootstrap.py[/dim]")
    console.print()

    console.print("[dim]Run 'drone @cli aipass init --help' for usage[/dim]")
    console.print()


def print_help():
    """Display Rich-formatted help for the init command."""
    from rich.panel import Panel
    from rich.table import Table
    from rich import box

    console.print()
    header("aipass init — Project Bootstrap")
    console.print("[dim]Initialize an AIPass project in any directory[/dim]")
    console.print()
    console.print("─" * 70)
    console.print()

    # Usage examples
    console.print("[bold cyan]USAGE:[/bold cyan]")
    console.print()

    usage_table = Table(show_header=False, border_style="dim", box=box.SIMPLE, padding=(0, 2))
    usage_table.add_column("Command", style="yellow")
    usage_table.add_column("Description", style="white")
    usage_table.add_row("drone @cli aipass init", "Initialize in current directory")
    usage_table.add_row("drone @cli aipass init /path/to/dir", "Initialize in target directory")
    usage_table.add_row("drone @cli aipass init /path MyProj", "Initialize with custom project name")
    console.print(usage_table)
    console.print()
    console.print("─" * 70)
    console.print()

    # What it creates
    console.print("[bold cyan]WHAT IT CREATES:[/bold cyan]")
    console.print()

    files_text = """[bold]Project scaffold (6 files):[/bold]

  [green]1.[/green] [yellow]{NAME}_REGISTRY.json[/yellow]       Project registry with UUID
  [green]2.[/green] [yellow].trinity/passport.json[/yellow]      Project identity (with registry_id)
  [green]3.[/green] [yellow].trinity/local.json[/yellow]         Session history & learnings
  [green]4.[/green] [yellow].trinity/observations.json[/yellow]  Collaboration patterns
  [green]5.[/green] [yellow].aipass/aipass_local_prompt.md[/yellow]  Local prompt (injected every turn)
  [green]6.[/green] [yellow]AIPASS.md[/yellow]                   Project prompt (persists in context)"""

    console.print(Panel(files_text, border_style="green", padding=(1, 2), box=box.ROUNDED))
    console.print()
    console.print("─" * 70)
    console.print()

    # Arguments
    console.print("[bold cyan]ARGUMENTS:[/bold cyan]")
    console.print()

    args_table = Table(show_header=True, header_style="bold cyan", border_style="dim")
    args_table.add_column("Argument", style="green")
    args_table.add_column("Required", style="yellow")
    args_table.add_column("Default", style="dim")
    args_table.add_column("Description", style="white")
    args_table.add_row("target_dir", "No", "Current directory", "Directory to initialize")
    args_table.add_row("project_name", "No", "Directory name", "Name for registry (auto-uppercased)")
    console.print(args_table)
    console.print()
    console.print("─" * 70)
    console.print()

    console.print("[dim]Commands: init, init --help[/dim]")
    console.print()


def handle_command(command: str, args: List[str]) -> bool:
    """Handle 'init' command.

    Args:
        command: The subcommand string (e.g. "init")
        args: Remaining positional arguments after the subcommand

    Returns:
        True if the command was handled, False otherwise
    """
    if command != "init":
        return False

    # Handle help flag
    if args and args[0] in ("--help", "-h", "help"):
        print_help()
        return True

    # Parse positional args: [target_dir] [project_name]
    caller_cwd = os.environ.get("AIPASS_CALLER_CWD", os.getcwd())
    target = Path(args[0]) if args else Path(caller_cwd)
    project_name = args[1] if len(args) > 1 else None

    try:
        result = init_project(target, project_name)
    except ValueError as exc:
        error(str(exc), suggestion="Pass a project name explicitly")
        sys.exit(1)
    except FileExistsError as exc:
        error(str(exc), suggestion="Remove the existing file to re-initialize")
        sys.exit(1)
    except OSError as exc:
        error(f"Filesystem error: {exc}")
        sys.exit(1)

    # Display results
    from rich.panel import Panel
    from rich.table import Table
    from rich import box

    console.print()
    header("Project Initialized")

    # Summary panel
    summary = (
        f"[bold]{result['project_name']}[/bold]\n"
        f"\n"
        f"  [yellow]Registry:[/yellow]  {result['registry_file']}\n"
        f"  [yellow]ID:[/yellow]        [dim]{result['registry_id'][:8]}...[/dim]\n"
        f"  [yellow]Target:[/yellow]    [dim]{result['target']}[/dim]"
    )
    console.print(Panel(summary, border_style="green", box=box.ROUNDED))

    # Files table
    files_table = Table(show_header=True, header_style="bold cyan", border_style="dim")
    files_table.add_column("#", style="green", width=3)
    files_table.add_column("File", style="yellow")
    for i, f in enumerate(result["created_files"], 1):
        files_table.add_row(str(i), f)
    console.print(files_table)
    console.print()

    success(f"Created {len(result['created_files'])} files")
    console.print()

    return True


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "handle_command",
]


# =============================================================================
# ENTRY POINT (SEED pattern)
# =============================================================================

if __name__ == "__main__":
    try:
        if len(sys.argv) == 1:
            print_introspection()
            sys.exit(0)

        if sys.argv[1] in ("--help", "-h", "help"):
            print_help()
            sys.exit(0)

        command = sys.argv[1]
        cmd_args = sys.argv[2:] if len(sys.argv) > 2 else []

        if handle_command(command, cmd_args):
            sys.exit(0)
        else:
            console.print(f"[red]Unknown command: {command}[/red]")
            console.print("[dim]Run 'python3 init_project.py --help' for usage[/dim]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
