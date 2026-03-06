#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: json_handler.py - JSON Handler (Canonical Path)
# Date: 2026-02-28
# Version: 1.0.0
# Category: ai_mail/handlers/json
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-02-28): Re-export from json_utils for Seed architecture compliance
#
# CODE STANDARDS:
#   - Re-exports json_handler from json_utils/ (canonical implementation)
#   - Satisfies Seed architecture standard for apps/handlers/json/ path
# =============================================

"""
JSON Handler - Canonical Path

Re-exports json_handler functions from json_utils/ to satisfy
the Seed architecture standard requiring apps/handlers/json/json_handler.py.
"""

from pathlib import Path

# Infrastructure paths
AIPASS_ROOT = Path.home() / "aipass_core"
AI_MAIL_ROOT = Path.home() / "aipass_core" / "ai_mail"
AI_MAIL_JSON_DIR = AI_MAIL_ROOT / "ai_mail_json"

from aipass.ai_mail.apps.handlers.json_utils.json_handler import (  # noqa: F401
    load_json,
    save_json,
    ensure_json_exists,
    get_json_path,
)
