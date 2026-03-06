#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: load.py - Registry Loading Handler
# Date: 2025-11-15
# Version: 1.0.0
# Category: ai_mail/handlers/registry
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2025-11-15): Initial handler - extracted from local_memory_monitor module
#
# CODE STANDARDS:
#   - Business logic implementation
#   - Pure functions where possible
#   - Clear error handling
# =============================================

"""
Registry Loading Handler - Loads registry files from disk.
"""

import json
from pathlib import Path
from typing import Dict


def load_registry(registry_file: Path) -> Dict:
    """
    Load branch registry from file.

    Args:
        registry_file: Path to the registry JSON file

    Returns:
        Registry dictionary with structure:
        {
            "last_updated": str,
            "active_branches": dict,
            "statistics": {
                "total_branches": int,
                "green_status": int,
                "yellow_status": int,
                "red_status": int
            }
        }
    """
    if not registry_file.exists():
        return {
            "last_updated": "",
            "active_branches": {},
            "statistics": {
                "total_branches": 0,
                "green_status": 0,
                "yellow_status": 0,
                "red_status": 0
            }
        }

    # Direct file read for registry (non-standard JSON location)
    with open(registry_file, 'r', encoding='utf-8') as f:
        return json.load(f)
