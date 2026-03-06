#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: __init__.py - Telegram Handlers Package
# Date: 2026-02-03
# Version: 1.0.0
# Category: api/handlers/telegram
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-02-03): Initial package for Telegram bridge
# =============================================

"""
Telegram Handlers Package

Provides Telegram bot integration for AIPass:
- config.py: Token and configuration loading
- bridge.py: Core bot service with message handling
"""

from aipass.api.apps.handlers.telegram.config import (
    load_telegram_config,
    get_bot_token,
    get_bot_username
)

__all__ = [
    "load_telegram_config",
    "get_bot_token",
    "get_bot_username"
]
