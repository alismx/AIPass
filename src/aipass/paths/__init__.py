"""
AIPass Paths — Root Resolution Module.

Foundation package. ZERO external dependencies.

Resolves the AIPass root directory using a 3-tier priority:
    1. AIPASS_ROOT environment variable (explicit — deployment/CI)
    2. .aipass/ marker directory walk (auto-detect — like git finding .git/)
    3. ~/.aipass/ default fallback (fresh install — XDG pattern)

All other modules derive paths from get_root():
    - system_logs_dir()      -> get_root() / "system_logs"
    - branch_registry_path() -> get_root() / "BRANCH_REGISTRY.json"
    - branch_path(name)      -> registry lookup, returns None if not found
    - branch_logs_dir(dir)   -> dir / "logs"

Exceptions:
    - PathResolutionError    -> raised when root cannot be resolved
"""

from __future__ import annotations

from .derived import branch_logs_dir, branch_path, branch_registry_path, system_logs_dir
from .exceptions import PathResolutionError
from .resolver import get_root

__version__ = "1.0.0"

__all__ = [
    # Core
    "get_root",
    # Derived paths
    "system_logs_dir",
    "branch_registry_path",
    "branch_path",
    "branch_logs_dir",
    # Exceptions
    "PathResolutionError",
]
