#!/home/aipass/.venv/bin/python3
# -*- coding: utf-8 -*-

# ===================AIPASS====================
# META DATA HEADER
# Name: list_templates.py
# Date: 2025-11-07
# Version: 1.1.0
# Category: flow/handlers/template
#
# CHANGELOG:
#   - v1.1.0 (2025-11-21): Removed Prax logging per 3-tier standard
#   - v1.0.0 (2025-11-07): Extracted from flow_template_handler.py
# =============================================

"""
List Templates Handler

Lists all available PLAN templates from template directories.

Features:
- Scans /home/aipass/aipass_core/templates/flow/
- Returns sorted list of template names
- Multi-directory support
- Reusable across Flow modules

Usage:
    from aipass.flow.apps.handlers.template.list_templates import list_templates

    templates = list_templates()
    print(f"Available: {templates}")  # ['default', 'master', ...]
"""

from pathlib import Path

# INFRASTRUCTURE IMPORT PATTERN
_PKG_ROOT = Path(__file__).resolve().parents[4]

# =============================================
# CONFIGURATION
# =============================================

MODULE_NAME = "list_templates"
TEMPLATES_DIR = _PKG_ROOT / "templates" / "flow"

# =============================================
# HELPER FUNCTIONS
# =============================================

def _template_search_dirs() -> list[Path]:
    """Determine the ordered list of directories to search for templates"""
    return [TEMPLATES_DIR]

# =============================================
# HANDLER FUNCTION
# =============================================

def list_templates() -> list[str]:
    """
    List all available templates across the configured template directories.

    Returns:
        List of template names (without .md extension), sorted alphabetically

    Example:
        >>> list_templates()
        ['default', 'master', 'api', 'webapp']
    """
    try:
        template_names: set[str] = set()
        search_dirs = _template_search_dirs()

        for base_dir in search_dirs:
            if not base_dir.exists():
                continue

            for template_file in base_dir.glob("*.md"):
                template_names.add(template_file.stem)

        sorted_templates = sorted(template_names)
        return sorted_templates

    except Exception:
        return []
