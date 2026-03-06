#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: read.py - Registry Read Handler
# Date: 2025-11-15
# Version: 1.0.0
# Category: ai_mail/handlers/registry
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2025-11-15): Extracted from ai_mail_cli.py
#
# CODE STANDARDS:
#   - Handlers are INDEPENDENT (no cross-domain imports)
#   - Use: from prax.apps.modules.logger import system_logger as logger
#   - Keep handlers <300 lines each
# =============================================

"""
Registry Read Handler

Handles reading branch registry data including:
- Reading all branches from BRANCH_REGISTRY.json
- Deriving email addresses from branch names
- Mapping email addresses to branch paths

Handler Independence:
- No module imports from ai_mail
- Only uses Prax logger and standard library
- Fully transportable and self-contained
"""

import json
from pathlib import Path
from typing import List, Dict

from aipass.cli.apps.modules import console

# Constants
MODULE_NAME = "registry.read"
BRANCH_REGISTRY_PATH = Path("/home/aipass/BRANCH_REGISTRY.json")


def get_all_branches() -> List[Dict]:
    """
    Get list of all branches for email selection.
    Reads from AIPass branch registry at /home/aipass/BRANCH_REGISTRY.json

    Returns:
        List of dicts with branch info:
        [{"name": "AIPASS.admin", "path": "/", "email": "@admin"}, ...]

    Note:
        Returns empty list if registry not found or on error.
    """
    branches = []

    if not BRANCH_REGISTRY_PATH.exists():
        return []

    try:
        with open(BRANCH_REGISTRY_PATH, 'r', encoding='utf-8') as f:
            registry_data = json.load(f)

        # Parse branch entries from JSON structure
        for branch in registry_data.get("branches", []):
            branch_name = branch.get("name", "")
            path = branch.get("path", "")

            if not branch_name or not path:
                continue

            # Derive email address from branch name
            email = _derive_email_from_branch_name(branch_name)

            branches.append({
                "name": branch_name,
                "path": path,
                "email": email
            })

        return branches

    except Exception as e:
        return []


def _derive_email_from_branch_name(branch_name: str) -> str:
    """
    Derive email address from branch name.

    Rules:
    - AIPASS.admin -> @admin (take part after dot)
    - AIPASS Workshop -> @aipass (take first word)
    - AIPASS-HELP -> @help (take second part to avoid collision)
    - BACKUP-SYSTEM -> @backup (take first part)
    - DRONE -> @drone (take whole name)

    Args:
        branch_name: Branch name from registry

    Returns:
        Email address in format "@email"
    """
    if '.' in branch_name:
        # Special case: AIPASS.admin -> admin
        email_part = branch_name.split('.')[-1].lower()
    elif ' ' in branch_name:
        # Handle spaces: take first word
        email_part = branch_name.split()[0].lower()
    elif '-' in branch_name and branch_name.split('-')[0] == 'AIPASS':
        # AIPASS-prefixed branches: use second part to avoid collision
        email_part = branch_name.split('-', 1)[1].lower()
    else:
        # Take first word before hyphen or whole name
        email_part = branch_name.split('-')[0].lower()

    return f"@{email_part}"


def get_branch_by_email(email: str) -> Dict | None:
    """
    Get branch information by email address.

    Args:
        email: Email address (e.g., "@admin")

    Returns:
        Branch dict with name, path, email or None if not found
    """
    branches = get_all_branches()

    for branch in branches:
        if branch["email"] == email:
            return branch

    return None


def get_branch_email_map() -> Dict[str, str]:
    """
    Get mapping of email addresses to branch names.

    Returns:
        Dict mapping email -> branch_name
        Example: {"@admin": "AIPASS.admin", "@flow": "FLOW"}
    """
    branches = get_all_branches()
    return {branch["email"]: branch["name"] for branch in branches}


def get_branch_path_map() -> Dict[str, str]:
    """
    Get mapping of email addresses to branch paths.

    Returns:
        Dict mapping email -> path
        Example: {"@admin": "/", "@flow": "/home/aipass/flow"}
    """
    branches = get_all_branches()
    return {branch["email"]: branch["path"] for branch in branches}


if __name__ == "__main__":
    console.print("\n" + "="*70)
    console.print("AI_MAIL HANDLER: registry/read.py")
    console.print("="*70)
    console.print("\nRegistry Read Handler")
    console.print()
    console.print("FUNCTIONS PROVIDED:")
    console.print("  - get_all_branches() -> List[Dict]")
    console.print("  - get_branch_by_email(email) -> Dict | None")
    console.print("  - get_branch_email_map() -> Dict[str, str]")
    console.print("  - get_branch_path_map() -> Dict[str, str]")
    console.print()
    console.print("TESTING:")

    branches = get_all_branches()
    console.print(f"\nLoaded {len(branches)} branches:")
    for branch in branches[:5]:  # Show first 5
        console.print(f"  {branch['email']:15} -> {branch['name']}")

    if len(branches) > 5:
        console.print(f"  ... and {len(branches) - 5} more")

    console.print("\n" + "="*70 + "\n")
