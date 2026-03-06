#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: restore_plan.py - PLAN restore module (reopen closed plans)
# Date: 2025-11-22
# Version: 1.3.0
# Category: flow/modules
#
# CHANGELOG (Max 5 entries):
#   - v1.3.0 (2025-11-22): Use NEWEST backup when multiple exist, show restore location in output
#   - v1.2.1 (2025-11-22): Fixed relative path handling (convert "flow" → absolute path)
#   - v1.2.0 (2025-11-22): Fixed recovery to restore plans to ORIGINAL location (not hardcoded flow)
#   - v1.1.0 (2025-11-22): Added auto-recovery from processed_plans
#   - v1.0.0 (2025-11-21): Initial creation - restore closed plans to open status
#
# CODE STANDARDS:
#   - Seed v3.0 compliant (imports, architecture, error handling)
# ==============================================

"""
Restore PLAN Module

Thin orchestrator for plan restore workflow (reopening closed plans).
All business logic delegated to handlers.

Usage:
    From flow.py: flow restore <number>
    Standalone: python3 restore_plan.py <number>
"""

import sys
from pathlib import Path
from typing import List
from shutil import copy2
from datetime import datetime, timezone

# INFRASTRUCTURE IMPORT PATTERN
_PKG_ROOT = Path(__file__).resolve().parents[3]  # file.py → modules/ → apps/ → flow/ → aipass/
FLOW_ROOT = _PKG_ROOT / "flow"

# External: Prax logger
from aipass.prax.apps.modules.logger import system_logger as logger

# JSON handler for operation tracking
from aipass.flow.apps.handlers.json import json_handler

# CLI services for display and error handling
from aipass.cli.apps.modules import console

# Internal: Registry handlers
from aipass.flow.apps.handlers.registry.load_registry import load_registry
from aipass.flow.apps.handlers.registry.save_registry import save_registry

# Internal: Plan handlers
from aipass.flow.apps.handlers.plan.validator import normalize_plan_number, validate_plan_exists
from aipass.flow.apps.handlers.plan.display import (
    format_restore_header,
    format_restore_error,
    format_restore_success,
    format_restore_usage_error
)

# Internal: Dashboard handlers
from aipass.flow.apps.handlers.dashboard.update_local import update_dashboard_local
from aipass.flow.apps.handlers.dashboard.push_central import push_to_plans_central

# =============================================
# CONFIGURATION
# =============================================

MODULE_NAME = "restore_plan"

# =============================================
# INTROSPECTION
# =============================================

def print_introspection():
    """Display module info and connected handlers"""
    console.print()
    console.print("[bold cyan]restore_plan Module[/bold cyan]")
    console.print()

    console.print("[yellow]Connected Handlers:[/yellow]")
    console.print()

    console.print("  [cyan]handlers/plan/[/cyan]")
    console.print("    [dim]- command_parser.py[/dim]")
    console.print("    [dim]- validator.py[/dim]")
    console.print("    [dim]- display.py[/dim]")
    console.print()

    console.print("  [cyan]handlers/registry/[/cyan]")
    console.print("    [dim]- load_registry.py[/dim]")
    console.print("    [dim]- save_registry.py[/dim]")
    console.print()

    console.print("  [cyan]handlers/dashboard/[/cyan]")
    console.print("    [dim]- update_local.py[/dim]")
    console.print("    [dim]- push_central.py[/dim]")
    console.print()

    console.print("[dim]Run 'python3 restore_plan.py --help' for usage[/dim]")
    console.print()

# =============================================
# RECOVERY FUNCTIONS
# =============================================

def recover_plan_from_backup(plan_key: str) -> tuple[bool, str]:
    """
    Attempt to recover a plan from processed_plans backup

    Args:
        plan_key: Normalized plan number (e.g., "0165")

    Returns:
        (success, message)
    """
    # Check processed_plans directory
    processed_plans = _PKG_ROOT / "backup_system" / "processed_plans"
    plan_file = processed_plans / f"FPLAN-{plan_key}.md"

    # CRITICAL: If base file doesn't exist, or if timestamp variants exist, use the NEWEST backup
    # This handles cases where plan was closed multiple times from different locations
    variants = list(processed_plans.glob(f"FPLAN-{plan_key}*.md"))
    if variants:
        # Sort by modification time, newest first
        variants.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        plan_file = variants[0]  # Use most recent backup
    elif not plan_file.exists():
        return False, f"FPLAN-{plan_key} not found in backups"

    # Read plan file to extract original location from header
    try:
        with open(plan_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse location from header (e.g., "**Location**: /home/aipass")
        original_location = None
        for line in content.split('\n')[:20]:  # Check first 20 lines
            if line.startswith("**Location**:"):
                original_location = line.split("**Location**:")[1].strip()
                break

        # If location not found in header, default to FLOW_ROOT
        if not original_location:
            original_location = str(FLOW_ROOT)

        # CRITICAL: Convert relative paths to absolute paths
        # If location is relative (like "flow"), resolve it
        if not original_location.startswith('/'):
            # Relative path - resolve it
            if original_location == "flow":
                original_location = str(FLOW_ROOT)
            elif original_location == "aipass_core":
                original_location = str(_PKG_ROOT)
            elif original_location == "seed":
                original_location = str(Path.home() / "seed")
            else:
                # Try resolving relative to _PKG_ROOT
                potential_path = _PKG_ROOT / original_location
                if potential_path.exists():
                    original_location = str(potential_path)
                else:
                    # Try relative to home
                    potential_path = Path.home() / original_location
                    if potential_path.exists():
                        original_location = str(potential_path)
                    else:
                        # Fallback to FLOW_ROOT
                        original_location = str(FLOW_ROOT)

        # Determine relative path
        original_path = Path(original_location)
        if original_path == FLOW_ROOT:
            relative_path = "flow"
        elif original_path == _PKG_ROOT:
            relative_path = "aipass_core"
        elif original_path == Path.home():
            relative_path = str(Path.home())
        else:
            try:
                relative_path = str(original_path.relative_to(Path.home()))
            except ValueError:
                relative_path = str(original_path)

    except Exception as e:
        # If parsing fails, default to FLOW_ROOT
        original_location = str(FLOW_ROOT)
        relative_path = "flow"

    # Copy file to ORIGINAL location (preserve backup)
    target = Path(original_location) / f"FPLAN-{plan_key}.md"
    copy2(plan_file, target)

    # Create minimal registry entry
    registry = load_registry()
    registry["plans"][plan_key] = {
        "location": original_location,
        "relative_path": relative_path,
        "file_path": str(target),
        "status": "closed",
        "created": datetime.now(timezone.utc).isoformat(),
        "subject": "Recovered from backup",
        "closed": datetime.now(timezone.utc).isoformat(),
        "closed_reason": "recovered_from_backup",
        "template_type": "default"
    }
    save_registry(registry)

    return True, f"Recovered FPLAN-{plan_key} from {plan_file.name} to {original_location}"

# =============================================
# RESTORE PLAN WORKFLOW
# =============================================

def restore_plan(plan_num: str | None) -> bool:
    """
    Orchestrate plan restore workflow (thin orchestrator)

    Restores a closed plan back to open status by updating registry metadata.
    Does NOT move files - file must already be at registered location.

    Delegates all business logic to handlers:
    - Validation: validator handler
    - Registry ops: registry handlers
    - Display: display handler

    Args:
        plan_num: Plan number (e.g., "0001" or "1" or "42")

    Returns:
        True if successful, False otherwise
    """
    if not plan_num:
        logger.warning(f"[{MODULE_NAME}] Plan number required for restore")
        console.print(format_restore_error("invalid_number", ""))
        return False

    try:
        # 0. AUTO-HEAL: Run registry scan to detect moved files (self-healing)
        from aipass.flow.apps.modules.registry_monitor import scan_plan_files
        scan_plan_files()  # Auto-detects files not in registry
        logger.info(f"[{MODULE_NAME}] Auto-heal scan completed")

        # 1. VALIDATE: Normalize plan number (handler)
        plan_key = normalize_plan_number(plan_num)

        # 2. LOAD DATA: Get registry (service)
        registry = load_registry()

        # 3. VALIDATE: Check plan exists (handler)
        exists, error_msg = validate_plan_exists(plan_key, registry)
        if not exists:
            # AUTO-RECOVERY: Try to recover from processed_plans
            console.print(f"[yellow]FPLAN-{plan_key} not in registry - attempting recovery...[/yellow]")
            recovered, recovery_msg = recover_plan_from_backup(plan_key)

            if recovered:
                console.print(f"[green]✓ {recovery_msg}[/green]")
                # Reload registry with recovered plan
                registry = load_registry()
                plan_info = registry["plans"][plan_key]
                plan_file = Path(plan_info.get("file_path", ""))
            else:
                logger.warning(f"[{MODULE_NAME}] {error_msg} - Recovery failed: {recovery_msg}")
                console.print(format_restore_error("not_found", plan_key))
                console.print(f"[dim]Recovery attempt: {recovery_msg}[/dim]")
                return False
        else:
            plan_info = registry["plans"][plan_key]
            plan_file = Path(plan_info.get("file_path", ""))

        # 4. VALIDATE: Check plan is closed
        if plan_info.get("status") != "closed":
            logger.warning(f"[{MODULE_NAME}] FPLAN-{plan_key} is already open")
            console.print(format_restore_error("already_open", plan_key))
            return False

        # 5. VALIDATE: Check file exists at registered location
        if not plan_file.exists():
            logger.warning(f"[{MODULE_NAME}] File not found at {plan_file}")
            console.print(format_restore_error("file_missing", plan_key))
            return False

        # 6. DISPLAY: Show plan info before restore (handler)
        console.print(format_restore_header(plan_key, plan_info))

        # 7. UPDATE REGISTRY: Restore to open status
        plan_info['status'] = 'open'

        # Remove all close-related metadata
        plan_info.pop('closed', None)
        plan_info.pop('closed_reason', None)
        plan_info.pop('memory_created', None)
        plan_info.pop('memory_created_date', None)
        plan_info.pop('memory_file', None)

        save_registry(registry)
        logger.info(f"[{MODULE_NAME}] Restored FPLAN-{plan_key} to open status")

        # 8. UPDATE DASHBOARDS: Sync dashboard files (handlers)
        dashboard_success = update_dashboard_local()
        central_success = push_to_plans_central()

        # Log dashboard update results (3-tier: modules log, handlers don't)
        if not dashboard_success:
            logger.warning(f"[{MODULE_NAME}] Failed to update DASHBOARD.local.json")
        if not central_success:
            logger.warning(f"[{MODULE_NAME}] Failed to update PLANS.central.json")

        # 9. DISPLAY: Success message with location (handler)
        restored_location = plan_info.get("location", "unknown")
        console.print(format_restore_success(plan_key, restored_location))

        # Fire trigger event for plan restore (optional - trigger module may not be available)
        try:
            from aipass.trigger.apps.modules.core import trigger
            trigger.fire('plan_restored', plan_number=plan_key, location=restored_location)
        except ImportError:
            logger.info(f"[{MODULE_NAME}] Trigger module not available, skipping event fire")

        return True

    except ValueError:
        error_msg = f"Invalid plan number: {plan_num}"
        logger.warning(f"[{MODULE_NAME}] {error_msg}")
        console.print(format_restore_error("invalid_number", plan_num))
        return False

    except Exception as e:
        error_msg = f"Error restoring plan: {e}"
        logger.error(f"[{MODULE_NAME}] {error_msg}")
        console.print(format_restore_error("general", details=str(e)))
        return False


def handle_command(command: str, args: List[str]) -> bool:
    """
    Handle command routing for restore_plan module (thin orchestrator)

    Delegates to handlers:
    - Argument parsing: command_parser handler
    - Workflow execution: restore_plan orchestrator
    - Error display: display handler

    Args:
        command: Command name
        args: Additional arguments

    Returns:
        bool indicating success or failure
    """
    # Check if this is our command
    if command != "restore":
        return False

    # Import parser here (after command check)
    from aipass.flow.apps.handlers.plan.command_parser import parse_restore_command_args

    # Log the operation
    json_handler.log_operation(
        "plan_restored",
        {"command": command, "args": args}
    )

    # 1. PARSE ARGS: Use command_parser handler
    plan_num, error = parse_restore_command_args(args)

    # 2. VALIDATE: Check for parsing errors
    if error:
        console.print(format_restore_usage_error())
        return False

    # 3. EXECUTE: Run workflow orchestrator
    success = restore_plan(plan_num=plan_num)

    # 4. RETURN: Result (restore_plan already handles all output)
    return success


# =============================================
# STANDALONE EXECUTION (for testing)
# =============================================

if __name__ == "__main__":
    # Show introspection when run without arguments
    if len(sys.argv) == 1:
        print_introspection()
        sys.exit(0)

    # Handle help flag
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        import argparse
        PARSER = argparse.ArgumentParser(
            description='Restore PLAN file to open status',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
COMMANDS:
  restore, restore_plan      Restore a closed plan to open status

USAGE:
  python3 restore_plan.py restore <plan_number>
  python3 restore_plan.py --help

EXAMPLES:
  # Restore a closed plan
  python3 restore_plan.py restore 42

  # Using plan number directly
  python3 restore_plan.py 42

NOTES:
  - Plan must be closed to restore
  - Plan file must exist at registered location
  - Only updates registry metadata (does not move files)
            """
        )
        PARSER.print_help()
        sys.exit(0)

    # Confirm logger connection
    logger.info("Prax logger connected to restore_plan")

    # Log standalone execution
    json_handler.log_operation(
        "plan_restored",
        {"command": "standalone"}
    )

    # Call handle_command with default
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    if not args:
        console.print(format_restore_usage_error())
        console.print("Run with --help for usage information")
        console.print()
        sys.exit(1)

    # If first arg is not command, assume it's plan number (backward compatibility)
    if args[0] not in ['restore', 'restore_plan']:
        args.insert(0, 'restore')

    result = handle_command(args[0], args[1:])
    # Result is True on success, False on failure
    if result:
        sys.exit(0)
    else:
        sys.exit(1)
