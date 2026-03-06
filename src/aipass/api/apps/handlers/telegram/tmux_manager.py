#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: tmux_manager.py - tmux Session Manager for Telegram Bridge
# Date: 2026-02-12
# Version: 1.2.0
# Category: api/handlers/telegram
#
# CHANGELOG (Max 5 entries):
#   - v1.2.0 (2026-03-01): Add AIPASS_SESSION_TYPE env var + auto /rename for Claude session identification
#   - v1.1.0 (2026-02-24): Add bot_id awareness — AIPASS_BOT_ID env var in tmux sessions
#   - v1.0.0 (2026-02-12): Initial - tmux session create/kill/send/list for persistent Claude sessions
#
# CODE STANDARDS:
#   - Pure functions with proper error raising
#   - No Prax imports (handler tier 3)
# =============================================

"""
tmux Session Manager for Telegram Bridge

Manages persistent Claude Code sessions in tmux:
- Create named sessions (telegram-{branch_name}) running Claude Code
- Inject messages via tmux send-keys -l (literal mode)
- Kill/list sessions
- Capture pane content for status display

Each tmux session runs `claude --permission-mode bypassPermissions` continuously.
Messages are injected via send-keys, responses captured via Stop hook.
"""

# Infrastructure
import sys
from pathlib import Path

import asyncio
import shutil
import subprocess
import time
from typing import List, Optional


# Constants
SESSION_PREFIX = "telegram-"
DEFAULT_BRANCH = "dev_central"
CLAUDE_BIN = str(Path.home() / ".local" / "bin" / "claude")
SEND_KEYS_DELAY = 0.5  # seconds between text injection and Enter


RENAME_DELAY = 3  # seconds to wait for Claude to initialize before /rename


def _session_name(branch_name: str) -> str:
    """Build tmux session name from branch name."""
    return f"{SESSION_PREFIX}{branch_name}"


def _send_rename(session_name: str, branch_name: str) -> None:
    """Send /rename to a tmux session after Claude initializes."""
    time.sleep(RENAME_DELAY)
    rename_cmd = f"/rename {branch_name.upper()}-telegram"
    subprocess.run(
        ["tmux", "send-keys", "-t", session_name, rename_cmd, "Enter"],
        capture_output=True,
    )


def has_tmux() -> bool:
    """Check if tmux is available on the system."""
    return shutil.which("tmux") is not None


def session_exists(branch_name: str) -> bool:
    """
    Check if a tmux session exists for the given branch.

    Args:
        branch_name: Branch name (e.g. 'dev_central')

    Returns:
        True if session is alive
    """
    name = _session_name(branch_name)
    result = subprocess.run(
        ["tmux", "has-session", "-t", name],
        capture_output=True,
    )
    return result.returncode == 0


def create_session(branch_name: str, branch_path: Path, *, bot_id: Optional[str] = None) -> bool:
    """
    Create a tmux session and launch Claude Code inside it.

    Session is named telegram-{branch_name} and starts in branch_path.
    Claude is launched with AIPASS_SESSION_TYPE=telegram and
    --permission-mode bypassPermissions. After initialization,
    sends /rename BRANCH-telegram for the /resume picker.

    Args:
        branch_name: Branch name for session naming
        branch_path: Working directory for Claude Code
        bot_id: Optional bot ID — sets AIPASS_BOT_ID env var in tmux session

    Returns:
        True if session was created successfully
    """
    name = _session_name(branch_name)

    if session_exists(branch_name):
        print("[INFO]", "Session %s already exists", name)
        return True

    if not branch_path.is_dir():
        print("[ERROR]", "Branch path does not exist: %s", branch_path)
        return False

    try:
        # Create detached tmux session
        result = subprocess.run(
            [
                "tmux", "new-session",
                "-d",                     # Detached
                "-s", name,               # Session name
                "-c", str(branch_path),   # Working directory
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("[ERROR]", "Failed to create tmux session %s: %s", name, result.stderr)
            return False

        # Set bot_id environment variable if provided
        if bot_id:
            subprocess.run(
                ["tmux", "set-environment", "-t", name, "AIPASS_BOT_ID", bot_id],
                capture_output=True,
                text=True,
            )

        # Launch Claude Code inside the session
        # Explicit cd guarantees CWD even if shell profile drifts it
        # AIPASS_SESSION_TYPE=telegram lets drone status label this session
        claude_cmd = (
            f"cd '{branch_path}' && "
            f"AIPASS_SESSION_TYPE=telegram {CLAUDE_BIN} --permission-mode bypassPermissions"
        )
        subprocess.run(
            ["tmux", "send-keys", "-t", name, claude_cmd, "Enter"],
            capture_output=True,
        )

        # Rename the Claude conversation for the /resume picker
        # Claude needs a few seconds to initialize before /rename works
        _send_rename(name, branch_name)

        print("[INFO]", "Created tmux session %s at %s", name, branch_path)
        return True

    except Exception as e:
        print("[ERROR]", "Error creating tmux session %s: %s", name, e)
        return False


async def send_message(branch_name: str, message: str) -> bool:
    """
    Inject a message into a tmux session via send-keys.

    Uses -l flag for literal mode (no shell interpretation).
    Sends text first, waits briefly, then sends Enter.

    Args:
        branch_name: Branch name identifying the session
        message: The message text to inject

    Returns:
        True if message was sent successfully
    """
    name = _session_name(branch_name)

    if not session_exists(branch_name):
        print("[ERROR]", "Session %s does not exist", name)
        return False

    try:
        # Send text literally (no shell interpretation)
        result = subprocess.run(
            ["tmux", "send-keys", "-t", name, "-l", message],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("[ERROR]", "Failed to send text to %s: %s", name, result.stderr)
            return False

        # Wait before sending Enter (prevents rapid keystroke issues)
        await asyncio.sleep(SEND_KEYS_DELAY)

        # Send Enter to submit the message
        result = subprocess.run(
            ["tmux", "send-keys", "-t", name, "Enter"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("[ERROR]", "Failed to send Enter to %s: %s", name, result.stderr)
            return False

        print("[INFO]", "Injected message into %s (%d chars)", name, len(message))
        return True

    except Exception as e:
        print("[ERROR]", "Error sending to tmux session %s: %s", name, e)
        return False


def kill_session(branch_name: str) -> bool:
    """
    Kill a tmux session for the given branch.

    Args:
        branch_name: Branch name identifying the session

    Returns:
        True if session was killed (or didn't exist)
    """
    name = _session_name(branch_name)

    if not session_exists(branch_name):
        print("[INFO]", "Session %s does not exist, nothing to kill", name)
        return True

    try:
        result = subprocess.run(
            ["tmux", "kill-session", "-t", name],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("[INFO]", "Killed tmux session %s", name)
            return True
        else:
            print("[ERROR]", "Failed to kill session %s: %s", name, result.stderr)
            return False

    except Exception as e:
        print("[ERROR]", "Error killing tmux session %s: %s", name, e)
        return False


def list_sessions() -> List[str]:
    """
    List all active telegram-* tmux sessions.

    Returns:
        List of branch names with active sessions
    """
    try:
        result = subprocess.run(
            ["tmux", "list-sessions", "-F", "#{session_name}"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return []

        sessions = []
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if line.startswith(SESSION_PREFIX):
                branch = line[len(SESSION_PREFIX):]
                if branch:
                    sessions.append(branch)

        return sessions

    except Exception:
        return []


def get_session_pane(branch_name: str) -> Optional[str]:
    """
    Capture current visible pane content from a tmux session.

    Args:
        branch_name: Branch name identifying the session

    Returns:
        Pane content as string, or None if session doesn't exist
    """
    name = _session_name(branch_name)

    if not session_exists(branch_name):
        return None

    try:
        result = subprocess.run(
            ["tmux", "capture-pane", "-t", name, "-p"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return result.stdout
        return None

    except Exception:
        return None
