
# ===================AIPASS====================
# META DATA HEADER
# Name: memory_threshold_exceeded.py - Memory Threshold Exceeded Event Handler
# Date: 2026-01-31
# Version: 1.0.0
# Category: trigger/handlers/events
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-01-31): Created - Phase 3 migration (FPLAN-0280)
#
# CODE STANDARDS:
#   - Follows AIPass Seed standards
#   - NO logger imports (causes infinite recursion in event handlers)
#   - NO print statements (handlers must be silent)
#   - Silent failure - catch all exceptions, pass
# =============================================

"""
Memory Threshold Exceeded Event Handler

Handles memory_threshold_exceeded events fired when a branch's memory file
exceeds the configured threshold (600 lines by default).

Sends compression notification to the affected branch via AI_Mail.

Event data expected:
    - branch: Branch name where threshold exceeded
    - branch_path: Path to branch root
    - file_name: Memory file name (e.g., local.json, observations.json)
    - file_path: Full path to the memory file
    - line_count: Current line count
    - threshold: Threshold that was exceeded
    - timestamp: When detected
"""

from datetime import datetime
from pathlib import Path
from typing import Any


# Path resolution not needed - this handler uses only event data passed in kwargs


def _build_compression_message(
    branch: str,
    file_name: str,
    line_count: int,
    threshold: int
) -> str:
    """
    Build compression notification message.

    Args:
        branch: Branch name
        file_name: Memory file that exceeded threshold
        line_count: Current line count
        threshold: Threshold that was exceeded

    Returns:
        Formatted message string with compression instructions
    """
    return f"""Memory file threshold exceeded - compression needed.

Branch: {branch}
File: {file_name}
Current lines: {line_count}
Threshold: {threshold}

---
COMPRESSION INSTRUCTIONS:

Target: Reduce to ~400 lines while preserving critical information.

Priority order (what to keep):
1. Top 25% (most recent): Keep mostly intact
2. Next 25%: Reduce slightly (combine related entries)
3. Next 25%: Reduce more (summary format)
4. Last 25% (oldest): Delete if needed for space

Always preserve:
- Session headers and dates
- Key achievements and milestones
- Critical errors and resolutions
- Important patterns and learnings

Safe to remove:
- Routine status updates
- Redundant information
- Low-value details
- Completed temporary tasks

Maintain chronological order (newest first).

---
After compression, verify the file still loads correctly.
"""


def handle_memory_threshold_exceeded(
    branch: str | None = None,
    branch_path: str | None = None,
    file_name: str | None = None,
    file_path: str | None = None,
    line_count: int | None = None,
    threshold: int | None = None,
    timestamp: str | None = None,
    **_kwargs: Any
) -> None:
    """
    Handle memory_threshold_exceeded event - send compression notification.

    Sends AI_Mail to affected branch with compression instructions when
    their memory file exceeds the configured threshold.

    Args:
        branch: Branch name where threshold exceeded - REQUIRED
        branch_path: Path to branch root
        file_name: Memory file name - REQUIRED
        file_path: Full path to the memory file
        line_count: Current line count - REQUIRED
        threshold: Threshold that was exceeded (defaults to 600)
        timestamp: When detected (defaults to now)
        **_kwargs: Additional event data (ignored)
    """
    try:
        # Validate required fields
        if not branch or not file_name or line_count is None:
            return

        # Import AI_Mail delivery
        try:
            from aipass.ai_mail.apps.handlers.email.delivery import deliver_email_to_branch
        except ImportError:
            return

        # Set defaults
        if not timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not threshold:
            threshold = 600

        # Build target and message
        target_branch = f"@{branch.lower()}"
        subject = f"[MEMORY] {file_name} exceeded {threshold} lines - compress needed"

        notification_message = _build_compression_message(
            branch=branch,
            file_name=file_name,
            line_count=line_count,
            threshold=threshold
        )

        # Build and deliver email
        email_data = {
            'from': '@trigger',
            'from_name': 'Trigger',
            'to': target_branch,
            'subject': subject,
            'message': notification_message,
            'timestamp': timestamp,
            'auto_execute': False,
            'priority': 'normal'
        }

        deliver_email_to_branch(target_branch, email_data)

    except Exception:
        pass
