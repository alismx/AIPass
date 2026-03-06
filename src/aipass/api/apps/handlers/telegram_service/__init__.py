# ===================AIPASS====================
# META DATA HEADER
# Name: __init__.py - Telegram Service Handler Package
# Date: 2026-02-03
# Version: 1.0.0
# Category: api/handlers
# CODE STANDARDS: Seed v1.0.0
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-02-03): Initial package
# =============================================

"""Telegram Service Handler - systemd control operations"""

from aipass.api.apps.handlers.telegram_service.service import (
    start_service,
    stop_service,
    get_status,
    get_logs,
    SERVICE_NAME,
)

__all__ = [
    "start_service",
    "stop_service",
    "get_status",
    "get_logs",
    "SERVICE_NAME",
]
