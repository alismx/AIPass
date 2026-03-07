"""
Help Consistency Checker Handler

Checks that seedgo.py help text doesn't mention removed flags.
Validates help documentation accuracy.
"""

# =================== META ====================
# Name: help_check.py
# Description: Help Consistency Checker Handler
# Version: 1.0.0
# Created: 2026-03-05
# Modified: 2026-03-05
# =============================================


from pathlib import Path
from typing import Dict

from aipass.seedgo.apps.standards.aipass.handlers.file import file_handler
from aipass.seedgo.apps.standards.aipass.handlers.config import ignore_handler


def check_help_consistency() -> Dict:
    """
    Check that seedgo.py help text doesn't mention removed flags

    Returns:
        Dict with check results
    """
    seedgo_file = Path(__file__).resolve().parents[5] / "apps" / "seedgo.py"  # seedgo root / apps / seedgo.py
    issues = []
    removed_flags = []

    if not seedgo_file.exists():
        return {
            'name': 'Help Consistency',
            'passed': False,
            'issues': ["seedgo.py not found"],
            'score': 0
        }

    # Read seedgo.py and check for removed flags in help text
    try:
        content = file_handler.read_file(str(seedgo_file))
        if content is None:
            return {
                'name': 'Help Consistency',
                'passed': False,
                'issues': ["Could not read seedgo.py"],
                'score': 0
            }

        # Check for mentions of removed flags in help section
        removed_flags = list(ignore_handler.get_deprecated_patterns().keys())

        for flag in removed_flags:
            if flag in content:
                # Check if it's in a help/documentation context
                for line_num, line in enumerate(content.split('\n'), 1):
                    if flag in line:
                        # Skip comments that explain removal
                        if "removed" in line.lower() or "deprecated" in line.lower():
                            continue
                        # Flag found in non-comment context
                        issues.append(
                            f"Line {line_num}: mentions {flag} "
                            f"(removed in audit v0.4.0)"
                        )

    except Exception as e:
        issues.append(f"Error reading file: {e}")

    return {
        'name': 'Help Consistency',
        'passed': len(issues) == 0,
        'issues': issues,
        'checked': [f"Scanned seedgo.py for: {', '.join(removed_flags)}"],
        'score': 100 if len(issues) == 0 else 0
    }
