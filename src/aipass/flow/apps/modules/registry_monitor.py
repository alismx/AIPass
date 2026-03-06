#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: registry_monitor.py - Registry auto-healing and file watching module
# Date: 2025-11-21
# Version: 2.0.0
# Category: flow/modules
#
# CHANGELOG (Max 5 entries):
#   - v2.0.0 (2026-01-20): Migrated to Trigger event system - fires events, doesn't handle
#   - v1.0.0 (2025-11-21): Initial port from archive_temp with Python watchdog integration
#
# CODE STANDARDS:
#   - Seed v3.0 compliant (imports, architecture, error handling)
#   - Module-level logging (3-tier pattern)
#   - Event-driven: fires trigger events, handlers in Trigger branch
# ==============================================

"""
Registry Monitor Module - Auto-Healing PLAN Registry

Monitors filesystem for PLAN file changes and fires trigger events.

Architecture (v2.0):
- PlanFileWatcher detects filesystem events via Python watchdog
- Events are fired via trigger.fire() (plan_file_created, plan_file_deleted, plan_file_moved)
- Trigger handlers in trigger/apps/handlers/events/plan_file.py update the registry
- Decoupled: Flow fires events, Trigger handles reactions

Features:
- Real-time file watching via Python watchdog
- Auto-detect file create/move/delete events
- Scan and heal registry (orphaned entries, missing files)
- Duplicate plan detection with auto-renumbering
- Metadata preservation on file moves

Usage:
    From flow.py: flow registry_monitor [scan|start|stop|status]
    Standalone: python3 registry_monitor.py [command]

Commands:
    scan    - One-time scan and heal registry
    heal    - Alias for scan
    start   - Start watchdog monitoring (runs until Ctrl+C)
    stop    - Stop watchdog monitoring
    status  - Show monitoring status
"""

import sys
import re
import os
import time
import threading
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timezone
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# INFRASTRUCTURE IMPORT PATTERN
_PKG_ROOT = Path(__file__).resolve().parents[3]  # file.py → modules/ → apps/ → flow/ → aipass/
FLOW_ROOT = _PKG_ROOT / "flow"

# External: Prax logger
from aipass.prax.apps.modules.logger import system_logger as logger

# JSON handler for operation tracking
from aipass.flow.apps.handlers.json import json_handler

# CLI services for display
from aipass.cli.apps.modules import console

# Registry handlers
from aipass.flow.apps.handlers.registry.load_registry import load_registry
from aipass.flow.apps.handlers.registry.save_registry import save_registry

# =============================================
# CONFIGURATION
# =============================================

MODULE_NAME = "registry_monitor"
ECOSYSTEM_ROOT = Path("/home/aipass")  # Start from /home/aipass, not root /
FLOW_JSON_DIR = FLOW_ROOT / "flow_json"

# PLAN file pattern
PLAN_PATTERN = re.compile(r'^FPLAN-\d{4}\.md$')

# Directories to ignore during monitoring
IGNORE_FOLDERS = {
    # Development and version control
    ".git", ".venv", "venv", "__pycache__", "node_modules",
    ".pytest_cache", "dist", "build", ".idea", ".vscode",

    # Backup and archive
    "backup", "backups", ".backup", "archive", ".archive",
    "backup_system", "archive_temp", "processed_plans",

    # Memory and admin
    "MEMORY_BANK", "admin", "aipass-help",

    # User directories
    ".local", "Downloads", "downloads",

    # System directories (permission issues)
    "proc", "sys", "dev", "run", "boot", "lost+found",
    "timeshift", "snapshots", ".snapshots"
}

# Global observer instance
_observer: Any = None
_observer_lock = threading.Lock()

# Event deduplication
_recent_events: List[Tuple[str, str, float]] = []  # [(event_type, plan_num, timestamp)]
DEDUPE_WINDOW = 2.0  # seconds

# =============================================
# FILE WATCHER CLASS
# =============================================

class PlanFileWatcher(FileSystemEventHandler):
    """Monitors PLAN file changes and fires trigger events"""

    def on_created(self, event):
        """Handle file creation events - fires trigger event"""
        if not event.is_directory and self._is_plan_file(str(event.src_path)):
            file_path = Path(str(event.src_path))
            plan_num = self._get_plan_number(file_path)

            if plan_num and not self._is_duplicate_event("created", plan_num):
                logger.info(f"[{MODULE_NAME}] New PLAN file detected: {file_path.name}")
                self._schedule_fire_created(file_path)

    def on_deleted(self, event):
        """Handle file deletion events - fires trigger event"""
        if not event.is_directory and self._is_plan_file(str(event.src_path)):
            file_path = Path(str(event.src_path))
            plan_num = self._get_plan_number(file_path)

            if plan_num and not self._is_duplicate_event("deleted", plan_num):
                logger.info(f"[{MODULE_NAME}] PLAN file deleted: {file_path.name}")
                self._schedule_fire_deleted(file_path)

    def on_moved(self, event):
        """Handle file move/rename events - fires trigger event"""
        if not event.is_directory and self._is_plan_file(str(event.dest_path)):
            src_path = Path(str(event.src_path))
            dest_path = Path(str(event.dest_path))
            plan_num = self._get_plan_number(dest_path)

            if plan_num and not self._is_duplicate_event("moved", plan_num):
                logger.info(f"[{MODULE_NAME}] PLAN file moved: {src_path.name} -> {dest_path}")
                self._schedule_fire_moved(src_path, dest_path)

    def _is_plan_file(self, file_path: str) -> bool:
        """Check if file is a PLAN file"""
        return PLAN_PATTERN.match(Path(file_path).name) is not None

    def _get_plan_number(self, file_path: Path) -> Optional[str]:
        """Extract plan number from filename (e.g., FPLAN-0001.md -> 0001)"""
        match = re.search(r'FPLAN-(\d{4})\.md$', file_path.name)
        return match.group(1) if match else None

    def _is_duplicate_event(self, event_type: str, plan_num: str) -> bool:
        """Check if this is a duplicate recent event"""
        global _recent_events
        now = time.time()

        # Clean old events
        _recent_events = [(et, pn, ts) for et, pn, ts in _recent_events
                         if now - ts < DEDUPE_WINDOW]

        # Check for duplicates
        for et, pn, ts in _recent_events:
            if et == event_type and pn == plan_num:
                return True

        # Add to recent events
        _recent_events.append((event_type, plan_num, now))
        return False

    def _schedule_fire_created(self, file_path: Path):
        """Schedule trigger event with delay to avoid duplicate events"""
        timer = threading.Timer(0.5, self._fire_plan_file_created, args=(file_path,))
        timer.start()

    def _schedule_fire_deleted(self, file_path: Path):
        """Schedule trigger event with delay to avoid duplicate events"""
        timer = threading.Timer(0.5, self._fire_plan_file_deleted, args=(file_path,))
        timer.start()

    def _schedule_fire_moved(self, src_path: Path, dest_path: Path):
        """Schedule trigger event with delay to avoid duplicate events"""
        timer = threading.Timer(0.5, self._fire_plan_file_moved, args=(src_path, dest_path))
        timer.start()

    def _fire_plan_file_created(self, file_path: Path):
        """Fire plan_file_created event - Trigger handles registry update"""
        try:
            from aipass.trigger.apps.modules.core import trigger
            trigger.fire('plan_file_created', path=str(file_path))
        except ImportError:
            logger.warning(f"[{MODULE_NAME}] Trigger not available - plan_file_created event not fired for {file_path.name}")

    def _fire_plan_file_deleted(self, file_path: Path):
        """Fire plan_file_deleted event - Trigger handles registry update"""
        try:
            from aipass.trigger.apps.modules.core import trigger
            trigger.fire('plan_file_deleted', path=str(file_path))
        except ImportError:
            logger.warning(f"[{MODULE_NAME}] Trigger not available - plan_file_deleted event not fired for {file_path.name}")

    def _fire_plan_file_moved(self, src_path: Path, dest_path: Path):
        """Fire plan_file_moved event - Trigger handles registry update"""
        try:
            from aipass.trigger.apps.modules.core import trigger
            trigger.fire('plan_file_moved', src_path=str(src_path), dest_path=str(dest_path))
        except ImportError:
            logger.warning(f"[{MODULE_NAME}] Trigger not available - plan_file_moved event not fired for {dest_path.name}")


# =============================================
# SCAN AND HEAL FUNCTION
# =============================================

def _fire_event(event_name: str, **kwargs) -> bool:
    """
    Fire a trigger event (internal helper)

    Args:
        event_name: Name of the event to fire
        **kwargs: Event data

    Returns:
        True if event fired successfully, False otherwise
    """
    try:
        from aipass.trigger.apps.modules.core import trigger
        trigger.fire(event_name, **kwargs)
        return True
    except ImportError:
        logger.warning(f"[{MODULE_NAME}] Trigger not available - {event_name} event not fired")
        return False


def scan_plan_files() -> Dict[str, Any]:
    """
    Scan ecosystem for PLAN files and fire events to heal registry

    Fires events for:
    - Missing registry entries (plan_file_created)
    - Orphaned entries (plan_file_deleted)
    - Location mismatches (plan_file_moved)
    - Duplicate plan numbers are auto-renumbered on filesystem, then fire plan_file_created

    Architecture (v2.0):
    - This function DETECTS changes and FIRES events
    - Trigger handlers in plan_file.py HANDLE the registry updates
    - Flow never touches registry directly during scan

    Returns:
        Dict with scan results and event stats
    """
    logger.info(f"[{MODULE_NAME}] Starting PLAN file scan from: {ECOSYSTEM_ROOT}")

    # Find all PLAN files (detect duplicates)
    plan_files: Dict[str, Path] = {}
    duplicates: Dict[str, List[Path]] = {}

    def handle_walk_error(error):
        """Handle permission errors during os.walk"""
        if not isinstance(error, PermissionError):
            logger.warning(f"[{MODULE_NAME}] Error during scan: {error}")

    # Use os.walk() with error handling
    for root, dirs, files in os.walk(str(ECOSYSTEM_ROOT), topdown=True, onerror=handle_walk_error):
        # Skip ignored directories (modify dirs in-place to prevent descent)
        dirs[:] = [d for d in dirs if not any(ignored in d for ignored in IGNORE_FOLDERS)]

        # Check for PLAN files in this directory
        for filename in files:
            if PLAN_PATTERN.match(filename):
                file_path = Path(root) / filename
                match = re.search(r'FPLAN-(\d{4})\.md$', filename)
                if match:
                    plan_number = match.group(1)

                    # Duplicate detection
                    if plan_number in plan_files:
                        if plan_number not in duplicates:
                            duplicates[plan_number] = [plan_files[plan_number]]
                        duplicates[plan_number].append(file_path)
                        logger.warning(f"[{MODULE_NAME}] Duplicate FPLAN-{plan_number} found: {file_path}")
                    else:
                        plan_files[plan_number] = file_path

    # Auto-renumber duplicates (keep first, renumber rest)
    renumbered: List[Dict[str, str]] = []
    if duplicates:
        logger.warning(f"[{MODULE_NAME}] Found {len(duplicates)} duplicate PLAN files")

        # Get next available plan number
        current_max = max(int(num) for num in plan_files.keys()) if plan_files else 0
        next_available = current_max + 1

        for plan_num, paths in duplicates.items():
            # Keep first occurrence, renumber the rest
            for dup_path in paths[1:]:  # Skip first path (already in plan_files)
                old_name = dup_path.name
                new_num = f"{next_available:04d}"
                new_name = f"FPLAN-{new_num}.md"
                new_path = dup_path.parent / new_name

                try:
                    # Rename file on filesystem
                    dup_path.rename(new_path)
                    logger.info(f"[{MODULE_NAME}] Auto-renumbered: {old_name} -> {new_name} at {dup_path.parent}")

                    # Add to plan_files with new number
                    plan_files[new_num] = new_path
                    renumbered.append({
                        "old_number": plan_num,
                        "new_number": new_num,
                        "path": str(new_path)
                    })

                    next_available += 1
                except Exception as e:
                    logger.error(f"[{MODULE_NAME}] Failed to renumber {old_name}: {e}")

    # Load current registry to compare (read-only - we don't modify it here)
    registry = load_registry()
    plans = registry.get("plans", {})

    # Track events fired
    added: List[str] = []
    updated: List[str] = []
    removed: List[str] = []

    # Fire events for missing files (not in registry)
    for plan_number, file_path in plan_files.items():
        if plan_number not in plans:
            # File exists but not in registry - fire created event
            if _fire_event('plan_file_created', path=str(file_path)):
                added.append(plan_number)
                logger.info(f"[{MODULE_NAME}] Fired plan_file_created for FPLAN-{plan_number}")
        else:
            # Check if location changed (file moved)
            current_path = plans[plan_number].get("file_path", "")
            if current_path != str(file_path):
                # Fire moved event
                if _fire_event('plan_file_moved', src_path=current_path, dest_path=str(file_path)):
                    updated.append(plan_number)
                    logger.info(f"[{MODULE_NAME}] Fired plan_file_moved for FPLAN-{plan_number}")

    # Fire events for orphaned registry entries (in registry but file doesn't exist)
    for plan_number in list(plans.keys()):
        if plan_number not in plan_files:
            # Registry entry but no file - fire deleted event
            file_path = plans[plan_number].get("file_path", f"FPLAN-{plan_number}.md")
            if _fire_event('plan_file_deleted', path=file_path):
                removed.append(plan_number)
                logger.info(f"[{MODULE_NAME}] Fired plan_file_deleted for FPLAN-{plan_number}")

    # Log event results
    if added or updated or removed or renumbered:
        logger.info(f"[{MODULE_NAME}] Events fired - Created: {len(added)}, Moved: {len(updated)}, Deleted: {len(removed)}, Renumbered: {len(renumbered)}")

    # Reload registry to get updated count (after handlers processed events)
    registry = load_registry()
    total_plans = len(registry.get("plans", {}))

    logger.info(f"[{MODULE_NAME}] Scan complete - {total_plans} PLAN files in registry")

    return {
        "total_plans": total_plans,
        "added": added,
        "updated": updated,
        "removed": removed,
        "renumbered": renumbered,
        "healing_performed": len(added) + len(updated) + len(removed) + len(renumbered) > 0
    }


# =============================================
# MONITOR CONTROL
# =============================================

def start_monitoring():
    """Start PLAN file monitoring with watchdog"""
    global _observer

    with _observer_lock:
        if _observer and _observer.is_alive():
            logger.info(f"[{MODULE_NAME}] Monitor already running")
            console.print("[yellow]Monitor is already running[/yellow]")
            return False

        try:
            observer = Observer()
            observer.schedule(PlanFileWatcher(), str(ECOSYSTEM_ROOT), recursive=True)
            observer.start()
            _observer = observer
            logger.info(f"[{MODULE_NAME}] PLAN file monitor started - watching {ECOSYSTEM_ROOT}")
            console.print(f"[green]✓[/green] Monitor started - watching {ECOSYSTEM_ROOT}")
            return True

        except Exception as e:
            logger.error(f"[{MODULE_NAME}] Error starting monitor: {e}")
            console.print(f"[red]Error starting monitor: {e}[/red]")
            return False


def stop_monitoring():
    """Stop PLAN file monitoring"""
    global _observer

    with _observer_lock:
        if _observer and _observer.is_alive():
            _observer.stop()
            _observer.join()
            _observer = None
            logger.info(f"[{MODULE_NAME}] PLAN file monitor stopped")
            console.print("[green]✓[/green] Monitor stopped")
            return True
        else:
            logger.info(f"[{MODULE_NAME}] Monitor is not running")
            console.print("[yellow]Monitor is not running[/yellow]")
            return False


def get_status() -> Dict[str, Any]:
    """Get monitoring status"""
    global _observer

    registry = load_registry()
    total_plans = len(registry.get("plans", {}))
    open_plans = sum(1 for p in registry.get("plans", {}).values() if p.get("status") == "open")

    with _observer_lock:
        is_running = _observer and _observer.is_alive()

    return {
        "module": MODULE_NAME,
        "version": "2.0.0",
        "monitoring_active": is_running,
        "watch_location": str(ECOSYSTEM_ROOT),
        "total_plans": total_plans,
        "open_plans": open_plans,
        "ignore_folders": len(IGNORE_FOLDERS)
    }


# =============================================
# COMMAND HANDLER
# =============================================

def handle_command(command: str, args: List[str]) -> bool:
    """
    Handle command routing for registry_monitor module

    Commands:
        scan    - One-time scan and heal
        heal    - Alias for scan
        start   - Start watchdog monitoring
        stop    - Stop watchdog monitoring
        status  - Show monitoring status

    Args:
        command: Command name
        args: Additional arguments

    Returns:
        True if command handled successfully, False otherwise
    """
    # Check if this is our command
    if command != "registry":
        return False

    # Get subcommand
    subcommand = args[0] if args else "status"

    # Log the operation
    json_handler.log_operation(
        "registry_monitor",
        {"command": command, "subcommand": subcommand}
    )

    if subcommand in ["scan", "heal"]:
        console.print(f"[bold]Scanning for PLAN files...[/bold]")
        result = scan_plan_files()

        console.print()
        console.print(f"[green]✓[/green] Scan complete")
        console.print(f"  • Total plans: {result['total_plans']}")
        console.print(f"  • Added: {len(result['added'])}")
        console.print(f"  • Updated: {len(result['updated'])}")
        console.print(f"  • Removed: {len(result['removed'])}")
        console.print(f"  • Renumbered: {len(result['renumbered'])}")

        if result['healing_performed']:
            console.print(f"\n[yellow]Registry healed - {len(result['added']) + len(result['updated']) + len(result['removed'])} changes[/yellow]")
        else:
            console.print(f"\n[dim]No changes needed - registry is healthy[/dim]")

        console.print()
        return True

    elif subcommand == "start":
        console.print(f"[bold]Starting registry monitor...[/bold]")
        console.print()

        # Run initial scan before starting monitor
        console.print("[dim]Running initial scan...[/dim]")
        scan_result = scan_plan_files()
        console.print(f"[dim]Found {scan_result['total_plans']} PLAN files[/dim]")
        console.print()

        success = start_monitoring()
        if success:
            console.print()
            console.print("[bold yellow]Monitor is running. Press Ctrl+C to stop.[/bold yellow]")
            console.print()

            # Keep script alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                console.print()
                console.print("[bold]Stopping monitor...[/bold]")
                stop_monitoring()
                console.print()

        return success

    elif subcommand == "stop":
        return stop_monitoring()

    elif subcommand == "status":
        status = get_status()

        console.print()
        console.print("[bold cyan]Registry Monitor Status[/bold cyan]")
        console.print()
        console.print(f"  • Version: {status['version']}")
        console.print(f"  • Monitoring: {'[green]Active[/green]' if status['monitoring_active'] else '[yellow]Inactive[/yellow]'}")
        console.print(f"  • Watch location: {status['watch_location']}")
        console.print(f"  • Total plans: {status['total_plans']}")
        console.print(f"  • Open plans: {status['open_plans']}")
        console.print(f"  • Ignored folders: {status['ignore_folders']}")
        console.print()
        console.print("[dim]Commands: scan | start | stop | status[/dim]")
        console.print()

        return True

    else:
        console.print(f"[red]Unknown subcommand: {subcommand}[/red]")
        console.print()
        console.print("Available commands:")
        console.print("  • scan    - One-time scan and heal registry")
        console.print("  • heal    - Alias for scan")
        console.print("  • start   - Start watchdog monitoring")
        console.print("  • stop    - Stop watchdog monitoring")
        console.print("  • status  - Show monitoring status")
        console.print()
        return False


# =============================================
# INTROSPECTION
# =============================================

def print_introspection():
    """Display module info and usage"""
    console.print()
    console.print("[bold cyan]registry_monitor Module[/bold cyan]")
    console.print()

    console.print("[yellow]Purpose:[/yellow]")
    console.print("  Auto-healing registry that keeps PLAN files synchronized with filesystem")
    console.print()

    console.print("[yellow]Features:[/yellow]")
    console.print("  • Real-time file watching (watchdog)")
    console.print("  • Auto-detect create/move/delete events")
    console.print("  • Scan and heal registry")
    console.print("  • Duplicate detection with auto-renumbering")
    console.print("  • Metadata preservation on moves")
    console.print()

    console.print("[yellow]Commands:[/yellow]")
    console.print("  • scan    - One-time scan and heal registry")
    console.print("  • heal    - Alias for scan")
    console.print("  • start   - Start watchdog monitoring (runs until Ctrl+C)")
    console.print("  • stop    - Stop watchdog monitoring")
    console.print("  • status  - Show monitoring status")
    console.print()

    console.print("[yellow]Connected Handlers:[/yellow]")
    console.print("  • [cyan]handlers/registry/load_registry.py[/cyan]")
    console.print("  • [cyan]handlers/registry/save_registry.py[/cyan]")
    console.print()

    console.print("[dim]Run 'python3 registry_monitor.py --help' for detailed usage[/dim]")
    console.print()


def print_help():
    """Print help information for registry_monitor module"""
    console.print()
    console.print("[bold cyan]registry_monitor.py[/bold cyan] - Auto-healing PLAN registry")
    console.print()
    console.print("[yellow]COMMANDS:[/yellow]")
    console.print("  scan     - One-time scan and heal registry")
    console.print("  heal     - Alias for scan")
    console.print("  start    - Start watchdog monitoring (runs until Ctrl+C)")
    console.print("  stop     - Stop watchdog monitoring")
    console.print("  status   - Show monitoring status")
    console.print()
    console.print("[yellow]USAGE:[/yellow]")
    console.print("  python3 registry_monitor.py scan")
    console.print("  python3 registry_monitor.py start")
    console.print("  python3 registry_monitor.py status")
    console.print("  python3 registry_monitor.py --help")
    console.print()
    console.print("[yellow]EXAMPLES:[/yellow]")
    console.print("  [dim]# Run one-time scan and heal[/dim]")
    console.print("  python3 registry_monitor.py scan")
    console.print()
    console.print("  [dim]# Start persistent monitoring[/dim]")
    console.print("  python3 registry_monitor.py start")
    console.print()
    console.print("  [dim]# Check monitoring status[/dim]")
    console.print("  python3 registry_monitor.py status")
    console.print()
    console.print("  [dim]# Stop monitoring[/dim]")
    console.print("  python3 registry_monitor.py stop")
    console.print()
    console.print("[yellow]FEATURES:[/yellow]")
    console.print("  - Auto-detect PLAN file changes (create/move/delete)")
    console.print("  - Preserve metadata on file moves (status, closed date, etc.)")
    console.print("  - Detect and fix orphaned registry entries")
    console.print("  - Auto-renumber duplicate plan numbers")
    console.print("  - System-wide scanning from /home/aipass")
    console.print("  - Ignore common directories (.git, backups, etc.)")
    console.print()


# =============================================
# STANDALONE EXECUTION
# =============================================

if __name__ == "__main__":
    # Show introspection when run without arguments
    if len(sys.argv) == 1:
        print_introspection()
        sys.exit(0)

    # Handle help flag
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        print_help()
        sys.exit(0)

    # Confirm logger connection
    logger.info("Prax logger connected to registry_monitor")

    # Log standalone execution
    json_handler.log_operation(
        "registry_monitor",
        {"command": "standalone"}
    )

    # Call handle_command
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    result = handle_command("registry_monitor", args)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)
