#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: override.py - Logger Override System
# Date: 2025-11-10
# Version: 1.0.0
# Category: prax/handlers/logging
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2025-11-10): Extracted from archive.temp/prax_handlers.py
# =============================================

"""
PRAX Logger Override

Global logging.getLogger() override for automatic log routing.
Intercepts logging.getLogger() calls and routes to module-specific logs.
"""

from pathlib import Path

import logging
from typing import Optional

# Import from prax config
from aipass.prax.apps.handlers.config.load import (
    DEFAULT_LOG_LEVEL,
    get_debug_prints_enabled
)

# Import logging setup
from aipass.prax.apps.handlers.logging.setup import setup_individual_logger

# Import introspection
from aipass.prax.apps.handlers.logging.introspection import get_calling_module

from rich.console import Console
console = Console()

# Store original logging functions for restoration
_original_getLogger = logging.getLogger
_original_basicConfig = logging.basicConfig

def enhanced_getLogger(name: Optional[str] = None) -> logging.Logger:
    """Enhanced getLogger that redirects to our individual module loggers

    This function replaces the standard logging.getLogger() globally.
    When any module calls logging.getLogger(), it automatically routes
    to the appropriate module-specific log file.

    Args:
        name: Logger name (usually ignored, we detect from stack)

    Returns:
        Logger configured to write to module-specific log files
    """
    # Only print debug info if enabled in config
    if get_debug_prints_enabled():
        print(f"[DEBUG] enhanced_getLogger called with name: {name}")

    # Get the original logger first
    original_logger = _original_getLogger(name)

    # Get calling module for our routing
    module_name = get_calling_module()
    if get_debug_prints_enabled():
        print(f"[DEBUG] Detected calling module: {module_name}")

    # If we can detect the module, add our custom handler
    if module_name != 'unknown_module':
        if get_debug_prints_enabled():
            print(f"[DEBUG] Setting up individual logger for: {module_name}")
        # Clear existing handlers to prevent console output
        original_logger.handlers.clear()

        # Get or create our individual logger for this module
        individual_logger = setup_individual_logger(module_name)

        # Copy the handler from our individual logger to the original logger
        for handler in individual_logger.handlers:
            original_logger.addHandler(handler)

        # Set appropriate level
        original_logger.setLevel(DEFAULT_LOG_LEVEL)

        # Prevent propagation to root logger (stops console output)
        original_logger.propagate = False

    return original_logger

def install_logger_override():
    """Install the enhanced getLogger function globally

    Replaces logging.getLogger with our enhanced version.
    After this, all logging.getLogger() calls are intercepted.
    """
    logging.getLogger = enhanced_getLogger
    print("[prax] Global logger override installed")

def restore_original_logger():
    """Restore original getLogger function

    Removes the override and restores standard Python logging behavior.
    """
    logging.getLogger = _original_getLogger
    print("[prax] Original logger function restored")

def is_override_active() -> bool:
    """Check if logger override is currently active

    Returns:
        True if override is installed, False if using original
    """
    return logging.getLogger != _original_getLogger
