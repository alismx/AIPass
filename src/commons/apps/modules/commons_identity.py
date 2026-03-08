# ===================AIPASS====================
# META DATA HEADER
# Name: commons_identity.py - Branch identity detection module
# Date: 2026-03-07
# Version: 1.0.0
# Category: commons/apps/modules
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-03-07): Ported from dev system (FPLAN-0411)
#
# CODE STANDARDS:
#   - Thin wrapper re-exporting from handlers/identity/identity_ops.py
#   - Maintains backward compatibility for all importers
#   - No sys.path manipulation
# =============================================

"""
Branch Identity Detection for The Commons

Thin wrapper that re-exports identity functions from
handlers/identity/identity_ops.py for backward compatibility.

Usage:
    from commons.apps.modules.commons_identity import get_caller_branch
"""

try:
    from aipass.prax.apps.modules.logger import system_logger as logger
except ImportError:
    import logging
    logger = logging.getLogger("commons.identity")

# Re-export all public functions for backward compatibility
from commons.apps.handlers.identity.identity_ops import (
    find_branch_root,
    get_branch_info_from_registry,
    get_caller_branch,
    extract_mentions,
    resolve_display_name,
)

__all__ = [
    "find_branch_root",
    "get_branch_info_from_registry",
    "get_caller_branch",
    "extract_mentions",
    "resolve_display_name",
]
