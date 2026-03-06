#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: confirmation.py - Plan Confirmation Handler
# Date: 2025-11-15
# Version: 0.4.0
# Category: flow/handlers/plan
#
# CHANGELOG (Max 5 entries):
#   - v0.4.0 (2026-01-22): Auto-confirm in non-TTY environments for autonomous workflows
#   - v0.3.0 (2025-11-21): Removed Prax logging per 3-tier standard
#   - v0.2.0 (2025-11-21): Added Prax logging for EOFError
#   - v0.1.0 (2025-11-15): Initial handler - user confirmation prompts
#
# CODE STANDARDS:
#   - Interactive user prompts
#   - Simple boolean returns
#   - No logging (3-tier architecture)
# =============================================

"""
Plan Confirmation Handler

User interaction and confirmation prompts for plan operations.
"""

import sys
from pathlib import Path

# Infrastructure
_PKG_ROOT = Path(__file__).resolve().parents[4]


def confirm_plan_deletion(plan_key: str) -> bool:
    """
    Prompt user to confirm plan deletion

    Displays interactive prompt asking user to confirm deletion.
    Accepts "yes" or "y" (case-insensitive) as confirmation.

    In non-interactive environments (no TTY), auto-confirms to support
    autonomous workflows and scripted operations.

    Args:
        plan_key: Normalized plan number (e.g., "0001")

    Returns:
        True if user confirmed deletion or non-interactive environment
        False if user cancelled

    Example:
        >>> if confirm_plan_deletion("0042"):
        ...     # User confirmed, proceed with deletion
        ...     pass
    """
    # Auto-confirm in non-interactive environments (autonomous workflows, CI/CD)
    if not sys.stdin.isatty():
        return True

    try:
        response = input(f"Close FPLAN-{plan_key}? (yes/no): ").strip().lower()
        return response in ['yes', 'y']
    except EOFError:
        # Fallback for edge cases where isatty() returns True but input fails
        return True
