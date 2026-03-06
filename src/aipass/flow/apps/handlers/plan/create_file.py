#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: create_file.py - Plan File Creation Handler
# Date: 2025-11-15
# Version: 0.1.0
# Category: flow/handlers/plan
#
# CHANGELOG (Max 5 entries):
#   - v0.1.0 (2025-11-15): Initial handler - plan file creation
#
# CODE STANDARDS:
#   - Validates before writing
#   - UTF-8 encoding
# =============================================

"""
Plan File Creation Handler

Creates plan files with validation and error handling.
"""

from pathlib import Path
from typing import Tuple


def create_plan_file(
    plan_file: Path,
    content: str
) -> Tuple[bool, str]:
    """
    Create plan file with validation

    Validates that file doesn't already exist, then writes
    content to the file using UTF-8 encoding.

    Args:
        plan_file: Full path to plan file (e.g., /path/to/PLAN0001.md)
        content: Formatted template content to write

    Returns:
        Tuple of (success, error_message)
        - success: True if file created successfully
        - error_message: Empty on success, error details on failure

    Validation:
        Returns failure if file already exists

    Example:
        >>> success, error = create_plan_file(
        ...     Path("/tmp/PLAN0001.md"),
        ...     "# PLAN 0001\\n\\nContent here"
        ... )
        >>> if not success:
        ...     print(error)
    """
    # Validate file doesn't exist
    if plan_file.exists():
        parent_name = plan_file.parent.name
        error_msg = f"{plan_file.name} already exists in {parent_name}/"
        return False, error_msg

    # Create file
    try:
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, ""
    except Exception as e:
        error_msg = f"Failed to create {plan_file}: {e}"
        return False, error_msg
