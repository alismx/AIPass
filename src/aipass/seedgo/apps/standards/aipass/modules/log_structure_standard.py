"""
Log Structure Standards Module

Provides condensed module logging structure standards for AIPass modules.
Run directly or via: seedgo log_structure
"""

# =================== META ====================
# Name: log_structure_standard.py
# Description: Log Structure Standards Module
# Version: 1.0.0
# Created: 2026-03-06
# Modified: 2026-03-06
# =============================================


import sys
from pathlib import Path
from typing import List

from aipass.prax import logger
from aipass.seedgo.apps.standards.aipass.handlers.json import json_handler
from aipass.seedgo.apps.standards.aipass.handlers.standards.log_structure_content import get_log_structure_standards

from aipass.cli import console, header


def print_introspection():
    """Display module info and connected handlers"""
    console.print()
    console.print("[bold cyan]Log Structure Standards Module[/bold cyan]")
    console.print()

    console.print("[yellow]Connected Handlers:[/yellow]")
    console.print()

    handlers_dir = Path(__file__).parent.parent / "handlers" / "standards"

    if handlers_dir.exists():
        console.print("  [cyan]handlers/standards/[/cyan]")
        console.print("    [dim]- log_structure_content.py[/dim]")
        console.print("    [dim]- log_structure_check.py[/dim]")
        console.print()

    console.print("[dim]Run 'python3 log_structure_standard.py --help' for usage[/dim]")
    console.print()


def print_help():
    """Print drone-compliant help output"""
    console.print()
    console.print("[bold cyan]Log Structure Standards Module[/bold cyan]")
    console.print("Module logging directory structure standards")
    console.print()

    console.print("[yellow]COMMANDS:[/yellow]")
    console.print("  Commands: log_structure, --help")
    console.print()
    console.print("  [cyan]log_structure[/cyan]   - Display log structure standards")
    console.print()

    console.print("[yellow]USAGE:[/yellow]")
    console.print("  seedgo log_structure")
    console.print("  python3 log_structure_standard.py")
    console.print("  python3 log_structure_standard.py --help")
    console.print()

    console.print("[yellow]EXAMPLES:[/yellow]")
    console.print("  [dim]# Via seedgo[/dim]")
    console.print("  seedgo log_structure")
    console.print()
    console.print("  [dim]# Standalone[/dim]")
    console.print("  python3 log_structure_standard.py")
    console.print()


def handle_command(command: str, args: List[str]) -> bool:
    """Handle 'log_structure' command"""
    if command != "log_structure":
        return False

    json_handler.log_operation(
        "standard_displayed",
        {"command": command, "args": args}
    )

    print_standard()
    return True


def print_standard():
    """Print log structure standards - orchestrates handler call"""
    console.print()
    header("Module Log Structure Standards")
    console.print()
    for line in get_log_structure_standards():
        console.print(f"  {line}")
    console.print()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_introspection()
        sys.exit(0)

    if sys.argv[1] in ['--help', '-h', 'help']:
        print_help()
        sys.exit(0)

    logger.info("Prax logger connected to log_structure_standard")

    json_handler.log_operation(
        "standard_displayed",
        {"command": "standalone"}
    )
    print_standard()
