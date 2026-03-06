#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: service.py - Telegram Service Handler
# Date: 2026-02-03
# Version: 1.0.0
# Category: api/handlers
# CODE STANDARDS: Seed v1.0.0
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-02-03): Initial handler - systemd service operations
# =============================================

"""
Telegram Service Handler

Low-level systemd operations for telegram-bridge service.
"""

import subprocess
from pathlib import Path
from typing import Tuple

SERVICE_NAME = "telegram-bridge"
LOG_FILE = Path.home() / "system_logs" / "telegram_bridge.log"


def start_service() -> Tuple[bool, str]:
    """
    Start the telegram-bridge service

    Returns:
        Tuple of (success, message)
    """
    result = subprocess.run(
        ["systemctl", "--user", "start", SERVICE_NAME],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return True, "Service started"
    return False, result.stderr.strip() if result.stderr else "Unknown error"


def stop_service() -> Tuple[bool, str]:
    """
    Stop the telegram-bridge service

    Returns:
        Tuple of (success, message)
    """
    result = subprocess.run(
        ["systemctl", "--user", "stop", SERVICE_NAME],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return True, "Service stopped"
    return False, result.stderr.strip() if result.stderr else "Unknown error"


def get_status() -> Tuple[str, str]:
    """
    Get telegram-bridge service status

    Returns:
        Tuple of (status_code, details)
        status_code: 'running', 'stopped', 'not_found', 'unknown'
    """
    result = subprocess.run(
        ["systemctl", "--user", "status", SERVICE_NAME],
        capture_output=True,
        text=True
    )

    output = result.stdout if result.stdout else result.stderr

    if "Active: active (running)" in output:
        return "running", output
    elif "Active: inactive (dead)" in output:
        return "stopped", output
    elif "could not be found" in output.lower():
        return "not_found", output
    return "unknown", output


def get_logs(lines: int = 30) -> Tuple[bool, str]:
    """
    Get recent service logs

    Args:
        lines: Number of recent lines to return

    Returns:
        Tuple of (success, log_content or error_message)
    """
    if not LOG_FILE.exists():
        return False, f"No log file found at {LOG_FILE}"

    try:
        with open(LOG_FILE, encoding="utf-8") as f:
            all_lines = f.readlines()
            recent = all_lines[-lines:] if len(all_lines) > lines else all_lines

        if not recent:
            return False, "Log file is empty"

        return True, "".join(recent)
    except OSError as e:
        return False, f"Failed to read logs: {e}"
