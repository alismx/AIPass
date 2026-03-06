#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: inbox_lock.py - Inbox File Lock Handler
# Date: 2026-02-09
# Version: 1.0.0
# Category: ai_mail/handlers/email
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-02-09): Initial implementation - fcntl.flock based inbox.json locking
#
# CODE STANDARDS:
#   - Handler independence: NO cross-domain imports
#   - Uses logging module for diagnostics
#   - Pure business logic only
# =============================================

"""
Inbox File Lock Handler

Provides exclusive file locking for inbox.json read-modify-write operations.
Uses fcntl.flock (POSIX advisory locks) to prevent concurrent write corruption.

Usage:
    with inbox_lock(inbox_file):
        data = json.load(open(inbox_file, encoding='utf-8'))
        # ... modify data ...
        json.dump(data, open(inbox_file, 'w', encoding='utf-8'))
"""

import fcntl
from pathlib import Path
from contextlib import contextmanager



@contextmanager
def inbox_lock(inbox_file: Path):
    """
    Context manager that acquires an exclusive lock on an inbox.json file.

    Uses a separate .inbox.lock file adjacent to inbox.json to hold the
    fcntl.flock advisory lock. This avoids issues with truncating the
    locked file itself during writes.

    Args:
        inbox_file: Path to the inbox.json file to lock

    Yields:
        None - lock is held for the duration of the with block

    Raises:
        OSError: If lock cannot be acquired
    """
    lock_file = inbox_file.parent / ".inbox.lock"
    lock_fd = None

    try:
        # Create/open lock file
        lock_fd = open(lock_file, 'w', encoding='utf-8')

        # Acquire exclusive lock (blocking - waits for other processes)
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX)
        yield

    finally:
        if lock_fd is not None:
            try:
                # Release lock
                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
                lock_fd.close()
            except Exception:
                try:
                    lock_fd.close()
                except Exception:
                    pass  # Best-effort close
