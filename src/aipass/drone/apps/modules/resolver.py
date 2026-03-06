"""
Branch resolution logic.

Resolves symbolic @branch names to absolute paths and metadata.
"""

from typing import Any, Dict, List, Optional

from aipass.drone.apps.handlers.exceptions import BranchNotFoundError
from .registry import get_all_branches, get_branch_by_name, load_registry


def normalize_branch_name(symbolic_name: str) -> str:
    """Normalize a symbolic branch name. Strips @ prefix if present."""
    if symbolic_name.startswith("@"):
        return symbolic_name[1:]
    return symbolic_name


def normalize_branch_arg(target: str) -> str:
    """Normalize @branch argument: strip @ prefix, lowercase."""
    return target.lstrip("@").lower()


def resolve_branch(symbolic_name: str) -> str:
    """Resolve a symbolic branch name to its absolute path.

    Args:
        symbolic_name: Branch name with or without @ prefix

    Returns:
        Absolute path to branch directory as string

    Raises:
        BranchNotFoundError: If branch not in registry
        RegistryNotFoundError: If registry file missing
    """
    registry = load_registry()

    name = normalize_branch_name(symbolic_name).lower()
    branch = registry.get("branches", {}).get(name)

    if branch is None:
        raise BranchNotFoundError(
            f"Branch '{symbolic_name}' not found in registry"
        )

    return branch["path"]


def branch_exists(symbolic_name: str) -> bool:
    """Check if a branch exists in the registry."""
    name = normalize_branch_name(symbolic_name).lower()
    branch = get_branch_by_name(name)
    return branch is not None


def get_branch_info(symbolic_name: str) -> Dict[str, Any]:
    """Get full metadata for a branch.

    Raises:
        BranchNotFoundError: If branch not in registry
    """
    registry = load_registry()

    name = normalize_branch_name(symbolic_name).lower()
    branch = registry.get("branches", {}).get(name)

    if branch is None:
        raise BranchNotFoundError(
            f"Branch '{symbolic_name}' not found in registry"
        )

    return branch


def list_branches(
    branch_type: Optional[str] = None,
    status: str = "active",
) -> List[str]:
    """List all registered branches, optionally filtered by type and status.

    Returns:
        List of branch names with @ prefix
    """
    branches = get_all_branches(branch_type=branch_type, status=status)
    return [f"@{branch['name']}" for branch in branches]
