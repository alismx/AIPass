#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: watcher.py - File System Watching
# Date: 2025-11-26
# Version: 1.2.0
# Category: prax/handlers/discovery
#
# CHANGELOG (Max 5 entries):
#   - v1.2.0 (2025-11-26): Removed MEMORY_BANK coupling - prax only watches Python files
#   - v1.1.0 (2025-11-26): Refactored as pure handler (no console output)
#   - v1.0.0 (2025-11-10): Extracted from archive.temp/prax_discovery.py
# =============================================

"""
PRAX File Watcher (Handler)

Pure worker that watches for new Python files and updates module registry.
Memory file handling moved to MEMORY_BANK's own watcher.

No console output - follows 3-tier handler pattern.
"""

from pathlib import Path

from datetime import datetime, timezone
from typing import Any

from watchdog.observers import Observer as WatchdogObserver
from watchdog.events import FileSystemEventHandler

# Import from prax config
from aipass.prax.apps.handlers.config.load import (
    ECOSYSTEM_ROOT,
    SYSTEM_LOGS_DIR
)

# Import from prax registry handlers
from aipass.prax.apps.handlers.registry.load import load_module_registry
from aipass.prax.apps.handlers.registry.save import save_module_registry

# Import filtering
from aipass.prax.apps.handlers.discovery.filtering import should_ignore_path

# Global observer instance
_observer: Any = None


class PythonFileWatcher(FileSystemEventHandler):
    """Watch for new Python files (pure handler)"""

    def on_created(self, event):
        """Handle new file creation events"""
        if not event.is_directory and str(event.src_path).endswith('.py'):
            py_file = Path(str(event.src_path))

            # Skip ignored paths
            if should_ignore_path(py_file):
                return

            module_name = py_file.stem

            # Skip if already in registry
            modules = load_module_registry()
            if module_name in modules:
                return

            # Add new module to registry
            try:
                relative_path = py_file.relative_to(ECOSYSTEM_ROOT)
            except ValueError:
                # File is outside ECOSYSTEM_ROOT, skip
                return

            modules[module_name] = {
                "file_path": str(py_file),
                "relative_path": str(relative_path),
                "log_file": str(SYSTEM_LOGS_DIR / f"prax_{module_name}.log"),
                "discovered_time": datetime.now(timezone.utc).isoformat(),
                "size": py_file.stat().st_size,
                "modified_time": datetime.fromtimestamp(py_file.stat().st_mtime).isoformat(),
                "enabled": True
            }

            # Save updated registry
            save_module_registry(modules)


def start_file_watcher():
    """Start watching for new Python files

    Starts watchdog observer to monitor ECOSYSTEM_ROOT for new Python modules.
    """
    global _observer

    if _observer and _observer.is_alive():
        return

    # Create watcher instance
    watcher = PythonFileWatcher()

    new_observer = WatchdogObserver()
    # Watch ecosystem root for Python files (recursive)
    new_observer.schedule(watcher, str(ECOSYSTEM_ROOT), recursive=True)

    new_observer.start()
    _observer = new_observer


def stop_file_watcher():
    """Stop the file watcher"""
    global _observer

    if _observer and _observer.is_alive():
        _observer.stop()
        _observer.join()
        _observer = None


def is_file_watcher_active() -> bool:
    """Check if file watcher is currently active

    Returns:
        True if watcher is running, False otherwise
    """
    return _observer is not None and _observer.is_alive()
