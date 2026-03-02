"""
Derived path functions for AIPass.

All functions derive their paths from get_root() and return Path objects.
No side effects beyond reading the filesystem.
"""

from __future__ import annotations

import json
from pathlib import Path

from .resolver import get_root


def system_logs_dir() -> Path:
    """
    Return the system logs directory.

    Returns:
        get_root() / "system_logs"
    """
    return get_root() / "system_logs"


def branch_registry_path() -> Path:
    """
    Return the path to BRANCH_REGISTRY.json.

    Returns:
        get_root() / "BRANCH_REGISTRY.json"
    """
    return get_root() / "BRANCH_REGISTRY.json"


def branch_path(name: str) -> Path | None:
    """
    Look up a branch by name in BRANCH_REGISTRY.json and return its path.

    Args:
        name: Branch name (without @ prefix).

    Returns:
        Absolute Path to the branch directory, or None if the branch is not
        found or the registry file does not exist.
    """
    registry_file = branch_registry_path()

    if not registry_file.exists():
        return None

    try:
        with open(registry_file, encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None

    branches = data.get("branches", {})
    entry = branches.get(name)
    if entry is None:
        return None

    raw_path = entry.get("path")
    if raw_path is None:
        return None

    return Path(raw_path)


def branch_logs_dir(branch_dir: Path) -> Path:
    """
    Return the logs directory for a given branch directory.

    Args:
        branch_dir: Absolute path to a branch directory.

    Returns:
        branch_dir / "logs"
    """
    return branch_dir / "logs"
