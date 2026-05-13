# =================== AIPass ====================
# Name: branches_handler.py
# Description: Remote branches handler — list remote branches
# Version: 1.0.0
# Created: 2026-05-12
# Modified: 2026-05-12
# =============================================

"""Remote branches handler — list remote branches."""

from __future__ import annotations

import subprocess

from aipass.prax import logger
from aipass.drone.apps.handlers.json import json_handler
from aipass.drone.apps.handlers.git.lock_handler import find_repo_root


def list_remote_branches() -> dict:
    """List remote branches with origin/ prefix stripped.

    Returns:
        Dict with branches list, count, and message.
    """
    repo_root = find_repo_root()

    try:
        result = subprocess.run(
            ["git", "branch", "-r"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
        )
    except (OSError, subprocess.SubprocessError) as exc:
        logger.error("git branch -r failed: %s", exc)
        return {"branches": [], "count": 0, "message": f"Failed to list branches: {exc}"}

    if result.returncode != 0:
        return {"branches": [], "count": 0, "message": f"git branch -r error: {result.stderr.strip()}"}

    branches = []
    for line in result.stdout.splitlines():
        name = line.strip()
        if not name or " -> " in name:
            continue
        if name.startswith("origin/"):
            name = name[len("origin/") :]
        branches.append(name)

    json_handler.log_operation("list_remote_branches", {"count": len(branches)})
    logger.info("Listed %d remote branches", len(branches))

    return {"branches": branches, "count": len(branches), "message": f"{len(branches)} remote branches"}
