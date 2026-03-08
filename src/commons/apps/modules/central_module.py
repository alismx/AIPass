# ===================AIPASS====================
# META DATA HEADER
# Name: central_module.py - Central File Push Module
# Date: 2026-03-07
# Version: 1.0.0
# Category: commons/apps/modules
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-03-07): Ported from dev system for AIPass public framework
#
# CODE STANDARDS:
#   - Orchestration only - NO business logic
#   - Imports from handlers/ for all data operations
#   - Module interface: handle_command(command, args) -> bool
# =============================================

"""
Central File Push Module

Thin router for the push-central command. Delegates to
handlers/central/central_writer.py to aggregate commons stats
and write COMMONS.central.json.

Handles: push-central command.
"""

from typing import List

try:
    from aipass.prax.apps.modules.logger import system_logger as logger
except ImportError:
    import logging
    logger = logging.getLogger("commons.central_module")

try:
    from aipass.cli.apps.modules import console
except ImportError:
    from rich.console import Console
    console = Console()

from commons.apps.handlers.central.central_writer import update_central


# =============================================================================
# COMMAND ROUTING
# =============================================================================

def handle_command(command: str, args: List[str]) -> bool:
    """
    Handle central file push commands.

    Args:
        command: Command name (push-central)
        args: Command arguments

    Returns:
        True if command handled, False otherwise
    """
    if command != "push-central":
        return False

    try:
        stats = update_central()
        branch_count = len(stats.get("branch_stats", {}))
        console.print(f"[green]Central file updated:[/green] {branch_count} branches")
        return True
    except Exception as e:
        logger.error(f"[commons] push-central failed: {e}")
        console.print(f"[red]Error:[/red] {e}")
        return True
