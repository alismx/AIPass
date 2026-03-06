#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: resolve_location.py - Plan Location Resolution Handler
# Date: 2025-11-29
# Version: 1.0.0
# Category: flow/handlers/plan
#
# CHANGELOG (Max 5 entries):
#   - v1.1.0 (2025-11-29): Removed Drone dependency - @ symbols pre-resolved by Drone before Flow receives args
#   - v1.0.0 (2025-11-29): Refactored to use drone module services
#   - v0.1.0 (2025-11-15): Initial handler - location resolution with @folder syntax
#
# CODE STANDARDS:
#   - Handler implements business logic
#   - No external dependencies - @ symbols pre-resolved by Drone
# =============================================

"""
Plan Location Resolution Handler

Resolves plan locations for explicit paths.
@ symbols are pre-resolved by Drone before Flow receives args.
Handles absolute paths, relative paths, and defaults to cwd.
"""

from pathlib import Path
from typing import Tuple


def resolve_plan_location(
    location: str | None,
    ecosystem_root: Path
) -> Tuple[bool, Path, str]:
    """
    Resolve plan location for explicit paths

    Handles two location types:
    1. Explicit path: Resolved to absolute path
    2. None: Defaults to current working directory

    Note: @ symbols are pre-resolved by Drone before Flow receives args.
    Flow only handles absolute/relative paths.

    Validates that resolved directory exists.

    Args:
        location: Target location (absolute/relative path, or None for cwd)
        ecosystem_root: Root directory (kept for API compatibility, not used)

    Returns:
        Tuple of (success, resolved_path, error_message)
        - success: False if directory doesn't exist
        - resolved_path: Absolute path to directory (or Path.cwd() on error)
        - error_message: Empty string on success, error details on failure

    Examples:
        >>> resolve_plan_location("/home/aipass/aipass_core/flow", Path("/home/aipass/aipass_core"))
        (True, Path("/home/aipass/aipass_core/flow"), "")

        >>> resolve_plan_location(None, Path("/home/aipass/aipass_core"))
        (True, Path.cwd(), "")

        >>> resolve_plan_location("/nonexistent", Path("/home/aipass/aipass_core"))
        (False, Path.cwd(), "Directory /nonexistent does not exist")
    """
    # Determine target directory
    if location:
        # Handle explicit path
        target_dir = Path(location).resolve()
    else:
        # Default to current working directory
        target_dir = Path.cwd()

    # Validate directory exists
    if not target_dir.exists():
        return False, Path.cwd(), f"Directory {target_dir} does not exist"

    return True, target_dir, ""
