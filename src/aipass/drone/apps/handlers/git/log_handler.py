# =================== AIPass ====================
# Name: log_handler.py
# Description: Git log handler
# Version: 1.0.0
# Created: 2026-05-12
# Modified: 2026-05-12
# =============================================

"""Git log handler."""

from __future__ import annotations

import subprocess

from aipass.prax import logger
from aipass.drone.apps.handlers.json import json_handler
from aipass.drone.apps.handlers.git.lock_handler import find_repo_root


def get_git_log(count: int = 10) -> dict:
    """Get recent git log entries."""
    repo_root = find_repo_root()

    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"-{count}"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
        )
    except (OSError, subprocess.SubprocessError) as exc:
        logger.error("git log failed: %s", exc)
        return {"entries": [], "count": 0, "message": f"git log failed: {exc}"}

    if result.returncode != 0:
        return {
            "entries": [],
            "count": 0,
            "message": f"git log error: {result.stderr.strip()}",
        }

    entries = [line for line in result.stdout.splitlines() if line.strip()]

    json_handler.log_operation("get_git_log", {"count": len(entries)})
    logger.info("Retrieved %d log entries", len(entries))

    return {"entries": entries, "count": len(entries), "message": f"{len(entries)} log entries"}
