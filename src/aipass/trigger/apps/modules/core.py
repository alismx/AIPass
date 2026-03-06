#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: core.py - Trigger Event Bus
# Date: 2026-02-03
# Version: 1.2.0
# Category: trigger/modules
#
# CHANGELOG (Max 5 entries):
#   - v1.2.0 (2026-02-03): Add deferred queue for nested event firing (fixes catch-up blocking)
#   - v1.1.4 (2026-02-03): Pass fire_event callback to handlers (enables error catch-up)
#   - v1.1.3 (2026-02-03): Disable lazy-start watchers entirely (inotify exhaustion - use prax monitor)
#   - v1.1.2 (2026-02-03): Also start system log watcher (fixes missing system_logs monitoring)
#
# CODE STANDARDS:
#   - Follows AIPass Seed standards
#   - Event bus pattern for system-wide events
#   - Lazy-start pattern from Prax logger
# =============================================

"""
Core Trigger class - Event bus for AIPass

Branches fire events, Trigger handles reactions.
Pattern: Like Prax logger but for events.
"""

import inspect
from pathlib import Path


from aipass.prax.apps.modules.logger import system_logger as logger

from typing import Callable


def _get_caller() -> str:
    """Get the calling module/file name"""
    stack = inspect.stack()
    for frame in stack[2:]:  # Skip _get_caller and fire
        filepath = frame.filename
        if 'trigger/apps/modules/core.py' not in filepath:
            # Extract meaningful name from path
            path = Path(filepath)
            # Try to get branch/module name
            parts = path.parts
            for i, part in enumerate(parts):
                if part in ('aipass_core', 'MEMORY_BANK'):
                    if i + 1 < len(parts):
                        return parts[i + 1]  # Return branch name
            return path.stem  # Fallback to filename
    return 'unknown'


class Trigger:
    """Event bus for AIPass system"""

    _handlers = {}
    _history = []  # Optional: track recent events
    _initialized = False
    _firing = False  # Recursion guard
    _deferred_queue = []  # Queue for events fired during handling
    _draining_deferred = False  # Prevents nested deferred processing
    _log_watcher_started = False  # Lazy-start flag for log watcher

    @classmethod
    def _ensure_initialized(cls):
        """Auto-register handlers on first use"""
        if not cls._initialized:
            try:
                from aipass.trigger.apps.handlers.events.registry import setup_handlers
                setup_handlers()
            except ImportError as e:
                logger.warning(f"[TRIGGER] Handlers not available: {e}")
            cls._initialized = True

    @classmethod
    def _ensure_log_watcher(cls):
        """Lazy-start log watcher - DISABLED to prevent inotify exhaustion.

        The lazy-start pattern causes each process to start its own watchers,
        exhausting the system's inotify instance limit (128 by default).

        Log watching should be done by a dedicated persistent process:
        - Use `prax monitor` for real-time log watching
        - Or use the catch-up pattern to scan logs on demand

        See ERROR 1b5dd1af for details on inotify exhaustion issue.
        """
        # DISABLED: Each process starting watchers exhausts inotify instances
        # The lock mechanism only prevented simultaneous starts, not accumulation
        # over time as processes start/stop throughout the day.
        #
        # Architecture decision: Log watching belongs in prax monitor (persistent)
        # not lazy-started in every trigger.fire() call.
        pass

    @classmethod
    def on(cls, event: str, handler: Callable):
        """Register handler for event"""
        cls._handlers.setdefault(event, []).append(handler)

    @classmethod
    def off(cls, event: str, handler: Callable):
        """Remove handler"""
        if event in cls._handlers and handler in cls._handlers[event]:
            cls._handlers[event].remove(handler)

    @classmethod
    def fire(cls, event: str, **data):
        """Fire event to all registered handlers

        Supports nested event firing via deferred queue - events fired during
        handler execution are queued and processed after current handler completes.
        """
        # If already firing, queue this event for later (prevents recursion, enables nesting)
        if cls._firing:
            cls._deferred_queue.append((event, data))
            return

        cls._firing = True
        try:
            cls._ensure_initialized()
            cls._ensure_log_watcher()
            handlers = cls._handlers.get(event, [])
            caller = _get_caller()
            logger.info(f"[TRIGGER] {caller} fired: {event}")
            logger.info(f"[TRIGGER] {len(handlers)} handlers responding")

            # Provide fire_event callback so handlers can fire events without importing
            data['fire_event'] = cls.fire

            for handler in handlers:
                try:
                    handler(**data)
                except Exception as e:
                    logger.error(f"[TRIGGER] Handler error for {event}: {e}")
        finally:
            cls._firing = False

            # Process deferred events iteratively (NOT recursively)
            # Each fire() during drain just appends to queue, loop picks it up
            if not cls._draining_deferred:
                cls._draining_deferred = True
                try:
                    while cls._deferred_queue:
                        deferred_event, deferred_data = cls._deferred_queue.pop(0)
                        cls._firing = True
                        try:
                            handlers = cls._handlers.get(deferred_event, [])
                            data_copy = dict(deferred_data)
                            data_copy['fire_event'] = cls.fire
                            for handler in handlers:
                                try:
                                    handler(**data_copy)
                                except Exception:
                                    pass  # Silent - avoid logger recursion
                        finally:
                            cls._firing = False
                finally:
                    cls._draining_deferred = False

    @classmethod
    def status(cls) -> dict:
        """Show registered handlers"""
        return {event: len(handlers) for event, handlers in cls._handlers.items()}


# Create instance for import
trigger = Trigger()
