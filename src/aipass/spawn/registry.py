"""BRANCH_REGISTRY.json CRUD operations."""

import json
from datetime import datetime
from pathlib import Path


def find_registry(start_path=None):
    """
    Find BRANCH_REGISTRY.json by walking up from start_path.
    Falls back to repo root or creates beside the spawned agent.

    Args:
        start_path: Directory to start searching from

    Returns:
        Path to BRANCH_REGISTRY.json
    """
    if start_path:
        current = Path(start_path).resolve()
        # Walk up looking for existing registry
        for parent in [current] + list(current.parents):
            candidate = parent / "BRANCH_REGISTRY.json"
            if candidate.exists():
                return candidate

    # Default: same directory as start_path or cwd
    base = Path(start_path).resolve() if start_path else Path.cwd()
    return base / "BRANCH_REGISTRY.json"


def load_registry(registry_path):
    """
    Load registry from JSON file. Returns empty schema if missing.

    Args:
        registry_path: Path to BRANCH_REGISTRY.json

    Returns:
        Dict with metadata and branches list
    """
    registry_path = Path(registry_path)
    if not registry_path.exists():
        return {
            "metadata": {
                "version": "1.0.0",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "total_branches": 0,
            },
            "branches": [],
        }

    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
        return data
    except (json.JSONDecodeError, IOError):
        return {
            "metadata": {
                "version": "1.0.0",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "total_branches": 0,
            },
            "branches": [],
        }


def save_registry(registry_path, data):
    """
    Save registry to JSON file. Auto-updates timestamp and sorts branches.

    Args:
        registry_path: Path to BRANCH_REGISTRY.json
        data: Registry dict to save

    Returns:
        True on success, False on error
    """
    registry_path = Path(registry_path)
    data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    if "branches" in data:
        data["branches"] = sorted(
            data["branches"], key=lambda b: b.get("name", "")
        )

    try:
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return True
    except (IOError, TypeError):
        return False


def add_to_registry(registry_path, branch_name, branch_path, profile, email, purpose=""):
    """
    Add a new branch entry to the registry.

    Args:
        registry_path: Path to BRANCH_REGISTRY.json
        branch_name: Uppercase branch name (e.g. "MY_AGENT")
        branch_path: Absolute path to branch directory
        profile: Profile string (e.g. "AIPass Workshop")
        email: Branch email (e.g. "@my_agent")
        purpose: Optional purpose description

    Returns:
        True if added, False if already exists or error
    """
    registry = load_registry(registry_path)

    # Check for duplicates
    for branch in registry.get("branches", []):
        if branch.get("name") == branch_name:
            return False

    today = datetime.now().strftime("%Y-%m-%d")
    entry = {
        "name": branch_name,
        "path": str(branch_path),
        "profile": profile,
        "description": purpose or "New agent - purpose TBD",
        "email": email,
        "status": "active",
        "created": today,
        "last_active": today,
    }

    registry["branches"].append(entry)
    registry["metadata"]["total_branches"] = len(registry["branches"])

    return save_registry(registry_path, registry)
