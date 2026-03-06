"""
Registry configuration management.

Locates AIPASS_REGISTRY.json using walk-up finder pattern.
Works in both pip-installed and development environments.
"""

import os
from pathlib import Path
from typing import Optional


_registry_path: Optional[Path] = None


def _find_registry() -> Path:
    """Find AIPASS_REGISTRY.json by walking up from this file's location.

    Search order:
    1. Explicitly set path via set_registry_path()
    2. AIPASS_REGISTRY environment variable
    3. Walk up from drone package location
    4. Walk up from cwd
    5. Default: ~/.aipass/AIPASS_REGISTRY.json
    """
    # Walk up from this file (works for pip editable installs)
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        candidate = parent / "AIPASS_REGISTRY.json"
        if candidate.exists():
            return candidate

    # Walk up from cwd (works for regular installs)
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        candidate = parent / "AIPASS_REGISTRY.json"
        if candidate.exists():
            return candidate

    # Fallback — use package-relative path (no filesystem assumptions)
    return Path(__file__).resolve().parents[4] / "AIPASS_REGISTRY.json"


def get_registry_path() -> Path:
    """Get the current registry path.

    Priority:
    1. Explicitly set path via set_registry_path()
    2. AIPASS_REGISTRY environment variable
    3. Walk-up finder from package location
    """
    global _registry_path

    if _registry_path is not None:
        return _registry_path

    env_path = os.environ.get("AIPASS_REGISTRY")
    if env_path:
        return Path(env_path)

    return _find_registry()


def set_registry_path(path: str | Path) -> None:
    """Set a custom registry path."""
    global _registry_path
    _registry_path = Path(path)


def reset_registry_path() -> None:
    """Reset registry path to default (useful for testing)."""
    global _registry_path
    _registry_path = None
