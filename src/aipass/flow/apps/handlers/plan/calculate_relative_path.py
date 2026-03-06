#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: calculate_relative_path.py - Relative Path Calculator
# Date: 2025-11-15
# Version: 0.1.0
# Category: flow/handlers/plan
#
# CHANGELOG (Max 5 entries):
#   - v0.1.0 (2025-11-15): Initial handler - relative path calculation
#
# CODE STANDARDS:
#   - Pure calculation logic
#   - No I/O or logging
# =============================================

"""
Relative Path Calculator

Calculates relative paths from ecosystem root for plan location display.
"""

from pathlib import Path


def calculate_relative_location(
    target_dir: Path,
    ecosystem_root: Path
) -> str:
    """
    Calculate relative location from ecosystem root

    Returns a string representation of target_dir relative to ecosystem_root.
    Special cases:
    - If target_dir == ecosystem_root, returns "root"
    - If target_dir outside ecosystem_root, returns absolute path string

    Args:
        target_dir: Absolute path to target directory
        ecosystem_root: Root directory for relative calculation

    Returns:
        Relative path string, "root" if same as ecosystem_root,
        or absolute path string if outside ecosystem_root

    Examples:
        >>> calculate_relative_location(
        ...     Path("/home/aipass/aipass_core/flow"),
        ...     Path("/home/aipass/aipass_core")
        ... )
        "flow"

        >>> calculate_relative_location(
        ...     Path("/home/aipass/aipass_core"),
        ...     Path("/home/aipass/aipass_core")
        ... )
        "root"

        >>> calculate_relative_location(
        ...     Path("/tmp/somewhere"),
        ...     Path("/home/aipass/aipass_core")
        ... )
        "/tmp/somewhere"
    """
    try:
        relative_location = str(target_dir.relative_to(ecosystem_root))

        # Special case: "." becomes "root" for clarity
        if relative_location == ".":
            relative_location = "root"

        return relative_location

    except ValueError:
        # target_dir is outside ecosystem_root
        return str(target_dir)
