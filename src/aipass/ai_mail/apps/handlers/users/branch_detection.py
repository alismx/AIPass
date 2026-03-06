#!/usr/bin/env python3

# =============================================
# META DATA HEADER
# Name: branch_detection.py - Branch Auto-Detection Handler
# Date: 2025-11-18
# Version: 1.0.0
# Category: ai_mail/handlers/users
#
# CHANGELOG:
#   - v1.0.0 (2025-11-18): Initial creation - PWD/CWD branch detection
#
# CODE STANDARDS:
#   - Handler independence: NO cross-domain imports
#   - Can import Prax modules (service providers)
#   - Pure business logic only
# =============================================

"""
Branch Auto-Detection Handler

Detects which branch is calling AI_MAIL based on PWD/CWD.
Walks up directory tree to find branch root (has [BRANCH].id.json file).
"""

# =============================================
# IMPORTS
# =============================================
import os
import json
from pathlib import Path
from typing import Dict

# =============================================
# CONSTANTS
# =============================================
BRANCH_REGISTRY_PATH = Path.home() / "BRANCH_REGISTRY.json"

# =============================================
# BRANCH DETECTION FUNCTIONS
# =============================================

def detect_branch_from_pwd() -> Dict | None:
    """
    Detect which branch is calling based on current working directory.

    Walks up directory tree from PWD to find branch root (directory with [BRANCH].id.json).
    Then looks up branch info in BRANCH_REGISTRY.json.

    Returns:
        Dict with branch info if detected:
        {
            "name": "SEED",
            "path": "/home/aipass/seed",
            "email": "@seed",
            "display_name": "Seed (Standards Branch)",
            ...
        }
        None if no branch detected
    """
    try:
        # Get current working directory
        cwd = Path.cwd()

        # Find branch root
        branch_root = find_branch_root(cwd)
        if not branch_root:
            return None

        # Get branch info from registry
        branch_info = get_branch_info_from_registry(branch_root)
        if not branch_info:
            return None

        return branch_info

    except Exception:
        return None


def find_branch_root(start_path: Path) -> Path | None:
    """
    Walk up directory tree to find branch root.

    Branch root = directory containing a [BRANCH_NAME].id.json file.
    Example: /home/aipass/seed/ contains SEED.id.json

    Args:
        start_path: Directory to start searching from (usually PWD)

    Returns:
        Path to branch root directory, or None if not found
    """
    current = start_path.resolve()

    # Walk up directory tree (max 10 levels to prevent infinite loop)
    for _ in range(10):
        # Check if this directory has a [BRANCH].id.json file
        for file in current.glob("*.id.json"):
            # Found a .id.json file - this is likely a branch root
            return current

        # Move up one level
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent

    return None


def get_branch_info_from_registry(branch_path: Path) -> Dict | None:
    """
    Look up branch information in BRANCH_REGISTRY.json by path.

    Args:
        branch_path: Path to branch directory

    Returns:
        Dict with branch info from registry, or None if not found
    """
    if not BRANCH_REGISTRY_PATH.exists():
        return None

    try:
        with open(BRANCH_REGISTRY_PATH, 'r', encoding='utf-8') as f:
            registry = json.load(f)

        # Normalize branch_path for comparison
        branch_path_str = str(branch_path.resolve())

        # Search registry for matching path
        for branch in registry.get("branches", []):
            if Path(branch["path"]).resolve() == Path(branch_path_str):
                # Found match - return branch info
                return branch

        return None

    except Exception:
        return None


def get_branch_display_name(branch_info: Dict) -> str:
    """
    Generate display name for branch from registry info.

    Args:
        branch_info: Branch dict from registry

    Returns:
        Display name string (e.g., "Seed (Standards Branch)")
    """
    name = branch_info.get("name", "Unknown")
    description = branch_info.get("description", "")

    if description and description != "New branch - purpose TBD":
        # Use description as context
        return f"{name.title()} ({description})"
    else:
        # Just use name
        return name.title()


def get_local_config_path(branch_path: Path, branch_name: str) -> Path:
    """
    Get path to local user_config.json for a branch.

    Args:
        branch_path: Path to branch directory
        branch_name: Branch name (e.g., "SEED", "DRONE")

    Returns:
        Path to local config file ([branch_name]_json/user_config.json)
    """
    branch_name_lower = branch_name.lower()
    return branch_path / f"{branch_name_lower}_json" / "user_config.json"


if __name__ == "__main__":
    from aipass.cli.apps.modules import console

    console.print("\n" + "="*70)
    console.print("BRANCH AUTO-DETECTION HANDLER")
    console.print("="*70)
    console.print("\nPURPOSE:")
    console.print("  Detects which branch is calling AI_MAIL based on PWD/CWD")
    console.print("  Walks up directory tree to find branch root")
    console.print()
    console.print("FUNCTIONS PROVIDED:")
    console.print("  - detect_branch_from_pwd() -> Dict | None")
    console.print("  - find_branch_root(start_path) -> Path | None")
    console.print("  - get_branch_info_from_registry(branch_path) -> Dict | None")
    console.print("  - get_branch_display_name(branch_info) -> str")
    console.print("  - get_local_config_path(branch_path) -> Path")
    console.print()
    console.print("HANDLER CHARACTERISTICS:")
    console.print("  ✓ Independent - no module dependencies")
    console.print("  ✓ Can import Prax (service provider)")
    console.print("  ✓ Pure business logic")
    console.print("  ✗ CANNOT import parent modules")
    console.print()
    console.print("DETECTION FLOW:")
    console.print("  1. Get current working directory (PWD)")
    console.print("  2. Walk up tree to find [BRANCH].id.json file")
    console.print("  3. Look up branch path in BRANCH_REGISTRY.json")
    console.print("  4. Return branch info (name, email, path, etc.)")
    console.print()
    console.print("="*70 + "\n")
