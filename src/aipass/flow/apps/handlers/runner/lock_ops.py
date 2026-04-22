# =================== AIPass ====================
# Name: lock_ops.py
# Description: Process lock file operations handler
# Version: 1.0.0
# Created: 2026-04-22
# Modified: 2026-04-22
# =============================================

"""
Lock File Operations Handler

Provides atomic lock file management for background runners.
Uses O_CREAT | O_EXCL to avoid TOCTOU races between existence check and write.

Usage:
    from aipass.flow.apps.handlers.runner.lock_ops import (
        acquire_lock, release_lock
    )
"""

import os
from pathlib import Path

from aipass.prax import logger

from aipass.flow.apps.handlers.json import json_handler


def try_create_lock(lock_file: Path) -> bool:
    """Atomically create lock file with current PID. Returns True on success."""
    try:
        fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        return True
    except FileExistsError:
        logger.info("Lock file already exists, cannot acquire: %s", lock_file)
        return False


def is_lock_stale(lock_file: Path) -> bool:
    """Check if existing lock file belongs to a dead process."""
    try:
        pid = int(lock_file.read_text(encoding="utf-8").strip())
        os.kill(pid, 0)
        logger.info("Another instance running (PID %d), lock valid: %s", pid, lock_file)
        return False
    except (ValueError, ProcessLookupError, PermissionError):
        logger.info("Stale lock found, taking over: %s", lock_file)
        return True


def acquire_lock(lock_file: Path) -> bool:
    """Try to acquire lock file. Returns True if acquired.

    Uses atomic O_CREAT | O_EXCL to avoid TOCTOU race.
    """
    if try_create_lock(lock_file):
        json_handler.log_operation("lock_acquired", {"lock_file": str(lock_file)})
        return True

    if not is_lock_stale(lock_file):
        return False

    try:
        lock_file.unlink()
    except OSError as exc:
        logger.warning("Failed to remove stale lock %s: %s", lock_file, exc)
        return False

    if not try_create_lock(lock_file):
        logger.info("Another process grabbed lock during retry: %s", lock_file)
        return False

    json_handler.log_operation("lock_acquired", {"lock_file": str(lock_file), "stale_recovery": True})
    return True


def release_lock(lock_file: Path) -> None:
    """Release the lock file."""
    try:
        lock_file.unlink(missing_ok=True)
    except OSError as exc:
        logger.warning("Failed to release lock file %s: %s", lock_file, exc)
