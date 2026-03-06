#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: file_ops.py - Plan File Operations Handler
# Date: 2025-11-15
# Version: 0.1.0
# Category: flow/handlers/plan
#
# CHANGELOG (Max 5 entries):
#   - v0.1.0 (2025-11-15): Initial handler - file deletion operations
#
# CODE STANDARDS:
#   - Check existence before operations
#   - Return status messages for logging
# =============================================

"""
Plan File Operations Handler

File system operations for plan files (deletion, etc.).
"""

from pathlib import Path
from typing import Tuple


def delete_plan_file(plan_file: Path) -> Tuple[bool, str]:
    """
    Delete plan file from filesystem

    Checks if file exists before attempting deletion.
    Returns different status based on whether file existed.

    Args:
        plan_file: Path to plan file

    Returns:
        Tuple of (deleted, status_message)
        - deleted: True if file existed and was deleted,
                   False if file didn't exist (warning case)
        - status_message: Formatted message for display/logging

    Example:
        >>> from pathlib import Path
        >>> deleted, msg = delete_plan_file(Path("/tmp/PLAN0001.md"))
        >>> if not deleted:
        ...     print(f"Warning: {msg}")
    """
    if plan_file.exists():
        plan_file.unlink()
        return True, f"[OK] Deleted file: {plan_file}"
    else:
        return False, f"[WARNING] File not found: {plan_file}"
