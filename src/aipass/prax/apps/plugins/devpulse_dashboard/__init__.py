# =================== AIPass ====================
# Name: __init__.py
# Description: Devpulse dashboard plugin for prax
# Version: 1.0.0
# Created: 2026-05-16
# Modified: 2026-05-16
# =============================================

"""Devpulse dashboard plugin.

Populates devpulse's DASHBOARD.local.json with custom sections:
git, session, dispatch (and optionally system_health).

Each section builder gathers data and calls write_section() to persist.
refresh() orchestrates all section builders in sequence.
"""

from .refresh import refresh

__all__ = ["refresh"]
