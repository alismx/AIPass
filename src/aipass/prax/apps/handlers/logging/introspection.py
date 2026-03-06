#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: introspection.py - Stack Introspection
# Date: 2025-11-10
# Version: 1.0.0
# Category: prax/handlers/logging
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2025-11-10): Extracted from archive.temp/prax_handlers.py
# =============================================

"""
PRAX Logging Introspection

Stack introspection for detecting calling modules and branch paths.
Used by logger_setup.py to route logs to correct files.
"""

from pathlib import Path
from typing import Optional

def get_calling_module() -> str:
    """Detect calling module from stack trace

    Returns:
        Module name (e.g., 'drone', 'flow', 'cortex') or 'unknown_module'
    """
    import inspect

    frame = inspect.currentframe()
    try:
        # Walk up the stack to find the calling module
        current_frame = frame
        frame_count = 0
        while current_frame and frame_count < 10:  # Limit to prevent infinite loop
            current_frame = current_frame.f_back
            frame_count += 1
            if current_frame:
                module_path = current_frame.f_globals.get('__file__', '')
                if module_path and module_path != __file__:
                    # Skip any frame that's from prax internal files
                    if ('/prax/apps/modules/logger.py' not in module_path and
                        '/prax/apps/handlers/' not in module_path and
                        'prax_logger.py' not in module_path and
                        'prax_handlers.py' not in module_path):
                        module_name = Path(module_path).stem
                        return module_name
        return 'unknown_module'
    finally:
        del frame

def get_calling_module_path() -> Optional[str]:
    """Detect calling module path from stack trace

    Returns:
        Full path to calling module file or None
    """
    import inspect

    frame = inspect.currentframe()
    try:
        # Walk up the stack to find the calling module
        current_frame = frame
        frame_count = 0
        while current_frame and frame_count < 10:
            current_frame = current_frame.f_back
            frame_count += 1
            if current_frame:
                module_path = current_frame.f_globals.get('__file__', '')
                if module_path and module_path != __file__:
                    # Skip any frame that's from prax internal files
                    if ('/prax/apps/modules/logger.py' not in module_path and
                        '/prax/apps/handlers/' not in module_path and
                        'prax_logger.py' not in module_path and
                        'prax_handlers.py' not in module_path):
                        return module_path
        return None
    finally:
        del frame

def detect_branch_from_path(module_path: str) -> Optional[str]:
    """Detect branch name from module file path

    Examples:
        /home/aipass/aipass_core/flow/apps/module.py → "aipass_core/flow"
        /home/aipass/aipass_core/cortex/apps/module.py → "aipass_core/cortex"
        /home/aipass/aipass_core/prax/apps/module.py → "aipass_core/prax"
        /home/aipass/other_dir/module.py → "other_dir"

    Returns:
        Branch path (e.g., "aipass_core/flow") or None
    """
    if not module_path:
        return None

    path = Path(module_path)
    parts = path.parts

    # Find /home/aipass in path
    try:
        aipass_idx = parts.index('aipass')

        # Check if this is aipass_core structure
        if aipass_idx + 1 < len(parts) and parts[aipass_idx + 1] == 'aipass_core':
            # For aipass_core, we want aipass_core/module_name format
            # e.g., /home/aipass/aipass_core/flow/apps/module.py → "aipass_core/flow"
            if aipass_idx + 2 < len(parts):
                module_folder = parts[aipass_idx + 2]
                # Make sure it's not just a file in aipass_core root
                if aipass_idx + 3 < len(parts):
                    return f"aipass_core/{module_folder}"
        else:
            # For other structures, return the folder after aipass
            # e.g., /home/aipass/some_project/module.py → "some_project"
            if aipass_idx + 1 < len(parts):
                potential_branch = parts[aipass_idx + 1]
                # Skip if it's a file directly in /home/aipass
                if aipass_idx + 2 < len(parts):
                    return potential_branch
    except ValueError:
        pass

    return None
