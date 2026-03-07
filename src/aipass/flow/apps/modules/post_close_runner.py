
# ===================AIPASS====================
# META DATA HEADER
# Name: post_close_runner.py - Background post-close processing
# Date: 2026-02-14
# Version: 1.1.0
# Category: flow/modules
#
# CHANGELOG (Max 5 entries):
#   - v1.1.0 (2026-02-14): Add lock file to prevent concurrent execution
#   - v1.0.0 (2026-02-14): Created - runs summary generation and mbank archival in background
#
# CODE STANDARDS:
#   - Seedgo v3.0 compliant (imports, architecture, error handling)
# ==============================================

"""
Post-Close Background Runner

Runs memory bank archival as a background process.
Called by close_plan.py via subprocess.Popen so the close command returns fast.

Uses a lock file to prevent concurrent execution - if another instance is
already running, this one exits silently (the running instance will pick up
all unprocessed plans since it scans ALL of them).

This script lives inside the flow branch so handler import guards allow it.

Note: This is a background utility script, not a command-routable module.
It has no handle_command() or --help because it is never invoked by users
or drone directly - only by close_plan.py via subprocess.
"""

import os
import sys
from pathlib import Path

# INFRASTRUCTURE IMPORT PATTERN
_PKG_ROOT = Path(__file__).resolve().parents[3]  # file.py → modules/ → apps/ → flow/ → aipass/
FLOW_ROOT = _PKG_ROOT / "flow"

# External: Prax logger
from aipass.prax.apps.modules.logger import system_logger as logger

MODULE_NAME = "post_close_runner"

LOCK_FILE = FLOW_ROOT / ".post_close_runner.lock"

# AI summarization removed — plans vectorized directly from backup_system/processed_plans/
# from aipass.flow.apps.handlers.summary.generate import generate_summaries
from aipass.flow.apps.handlers.mbank.process import process_closed_plans


def _acquire_lock() -> bool:
    """Try to acquire lock file. Returns True if acquired, False if another instance is running."""
    if LOCK_FILE.exists():
        try:
            pid = int(LOCK_FILE.read_text().strip())
            os.kill(pid, 0)  # Signal 0 = check if process exists
            logger.info(f"[{MODULE_NAME}] Another instance running (PID {pid}), exiting")
            return False
        except (ValueError, ProcessLookupError, PermissionError):
            logger.info(f"[{MODULE_NAME}] Stale lock found, taking over")

    LOCK_FILE.write_text(str(os.getpid()))
    return True


def _release_lock():
    """Release the lock file."""
    try:
        LOCK_FILE.unlink(missing_ok=True)
    except OSError as e:
        logger.warning(f"[{MODULE_NAME}] Failed to release lock file: {e}")


if __name__ == "__main__":
    if not _acquire_lock():
        sys.exit(0)

    try:
        # generate_summaries() — removed, AI summarization no longer needed
        process_closed_plans()
    except Exception as e:
        logger.error(f"[{MODULE_NAME}] Background processing failed: {e}")
    finally:
        _release_lock()
