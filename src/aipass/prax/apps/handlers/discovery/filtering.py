#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: filtering.py - Path Filtering
# Date: 2025-11-10
# Version: 1.0.0
# Category: prax/handlers/discovery
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2025-11-10): Extracted from archive.temp/prax_discovery.py
# =============================================

"""
PRAX Discovery Filtering

Path filtering for module discovery using ignore patterns.
"""

from pathlib import Path

# Import from prax config
from aipass.prax.apps.handlers.config.ignore_patterns import load_ignore_patterns_from_config

def should_ignore_path(path: Path) -> bool:
    """Check if path should be ignored based on patterns from config

    Args:
        path: Path to check against ignore patterns

    Returns:
        True if path should be ignored, False otherwise
    """
    path_parts = path.parts  # Keep original case for exact matching

    # Load ignore patterns from config (with fallback to hardcoded)
    ignore_patterns = load_ignore_patterns_from_config()

    # Check against ignore patterns
    for part in path_parts:
        if part in ignore_patterns:
            return True

    return False
