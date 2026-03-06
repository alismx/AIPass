
# ===================AIPASS====================
# META DATA HEADER
# Name: memory_template_updated.py - Memory Template Updated Event Handler
# Date: 2026-02-14
# Version: 1.0.0
# Category: trigger/handlers/events
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-02-14): Created - Phase 3 of FPLAN-0340
#     * Handles memory_template_updated event
#     * Pushes living template updates to all branches
#
# CODE STANDARDS:
#   - Follows AIPass Seed standards
#   - NO logger imports (causes infinite recursion in event handlers)
#   - NO print statements (handlers must be silent)
#   - Silent failure - catch all exceptions, pass
# =============================================

"""
Memory Template Updated Event Handler

Handles memory_template_updated events fired when a living template
is modified. Pushes structural updates to all registered branches.

Event data expected:
    - template_name: Name of the updated template (optional)
    - updated_by: Who triggered the update (optional)
    - timestamp: When the update occurred (optional)
"""

from pathlib import Path
from typing import Any


# Path resolution not needed - this handler delegates to Memory Bank's pusher


def handle_memory_template_updated(**kwargs: Any) -> None:
    """
    Handle memory_template_updated event - push templates to all branches.

    Imports and calls push_templates() from Memory Bank's pusher handler.
    All operations are wrapped in try/except for silent failure.

    Args:
        **kwargs: Event data (template_name, updated_by, timestamp, etc.)
    """
    try:
        from aipass.memory_bank.apps.handlers.templates.pusher import push_templates
        push_templates(dry_run=False)
    except Exception:
        pass
