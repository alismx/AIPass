# =================== AIPass ====================
# Name: session_section.py
# Description: Session info section builder for devpulse dashboard
# Version: 1.0.0
# Created: 2026-05-16
# Modified: 2026-05-16
# =============================================

"""Session section builder for devpulse dashboard plugin.

Reads .trinity/local.json to extract current session ID, date,
active tasks, and last session summary. Writes to dashboard
via write_section().
"""

import json
from pathlib import Path
from typing import Dict

from aipass.prax.apps.modules.dashboard import write_section
from aipass.prax.apps.modules.logger import system_logger as logger


def build_session_section(branch_path: Path) -> bool:
    """Build session section data and write to dashboard.

    Args:
        branch_path: Path to devpulse branch root.

    Returns:
        True if write_section succeeded, False otherwise.
    """
    local_json_path = branch_path / ".trinity" / "local.json"

    if not local_json_path.exists():
        section_data: Dict = {
            "managed_by": "devpulse",
            "current_session": "unknown",
            "session_date": "",
            "today_focus": "",
            "active_tasks": [],
            "last_session_summary": "",
        }
        return write_section(branch_path, "session", section_data)

    try:
        data = json.loads(local_json_path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to read local.json at %s: %s", local_json_path, exc)
        section_data = {
            "managed_by": "devpulse",
            "current_session": "error",
            "session_date": "",
            "today_focus": "",
            "active_tasks": [],
            "last_session_summary": "Failed to read local.json",
        }
        return write_section(branch_path, "session", section_data)

    # Extract latest session (first in list = newest)
    sessions = data.get("sessions", [])
    current_session = ""
    session_date = ""
    last_session_summary = ""

    if sessions:
        latest = sessions[0]
        current_session = latest.get("id", "")
        session_date = latest.get("d", "")
        last_session_summary = latest.get("sum", "")

    # Extract active tasks
    active_tasks_data = data.get("active_tasks", {})
    today_focus = active_tasks_data.get("today_focus", "")
    pending = active_tasks_data.get("pending", [])

    section_data = {
        "managed_by": "devpulse",
        "current_session": current_session,
        "session_date": session_date,
        "today_focus": today_focus,
        "active_tasks": pending,
        "last_session_summary": last_session_summary,
    }

    return write_section(branch_path, "session", section_data)
