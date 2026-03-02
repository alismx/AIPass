"""
Root resolution logic for AIPass paths.

Resolves the AIPass root directory using a 3-tier priority:
    1. AIPASS_ROOT environment variable (if set and valid directory)
    2. .aipass/ marker directory walk (like git finding .git/)
    3. ~/.aipass/ default fallback (created if it doesn't exist)
"""

from __future__ import annotations

import os
from pathlib import Path

from .exceptions import PathResolutionError


def _resolve_from_env() -> Path | None:
    """
    Attempt to resolve root from AIPASS_ROOT environment variable.

    Returns:
        Path if env var is set and points to a valid directory, None otherwise.

    Raises:
        PathResolutionError: If env var is set but points to a non-existent directory.
    """
    env_val = os.environ.get("AIPASS_ROOT")
    if not env_val:  # None or empty string → not set
        return None

    candidate = Path(env_val)
    if not candidate.is_dir():
        raise PathResolutionError(
            f"AIPASS_ROOT environment variable points to a non-existent directory: {env_val!r}"
        )
    return candidate


def _resolve_from_marker(start: Path | None = None) -> Path | None:
    """
    Walk up the directory tree from start looking for a directory containing .aipass/.

    Args:
        start: Directory to start from. Defaults to Path.cwd().

    Returns:
        The directory that contains a .aipass/ subdirectory, or None if not found.
    """
    current = (start or Path.cwd()).resolve()

    for candidate in [current, *current.parents]:
        if (candidate / ".aipass").is_dir():
            return candidate

    return None


def _resolve_default() -> Path:
    """
    Return the default fallback root (~/.aipass/), creating it if needed.

    Returns:
        Path to ~/.aipass/, guaranteed to exist.
    """
    default = Path.home() / ".aipass"
    default.mkdir(parents=True, exist_ok=True)
    return default


def get_root(start: Path | None = None) -> Path:
    """
    Resolve the AIPass root directory using 3-tier priority.

    Priority order:
        1. AIPASS_ROOT environment variable (if set and valid)
        2. .aipass/ marker directory walk (starting from CWD or start)
        3. ~/.aipass/ default fallback (created if missing)

    Args:
        start: Optional starting directory for marker walk. Defaults to Path.cwd().

    Returns:
        Resolved AIPass root directory as an absolute Path.

    Raises:
        PathResolutionError: If AIPASS_ROOT env var is set but points to a non-existent directory.
    """
    # Tier 1: environment variable
    env_root = _resolve_from_env()
    if env_root is not None:
        return env_root

    # Tier 2: marker walk
    marker_root = _resolve_from_marker(start)
    if marker_root is not None:
        return marker_root

    # Tier 3: default fallback
    return _resolve_default()
