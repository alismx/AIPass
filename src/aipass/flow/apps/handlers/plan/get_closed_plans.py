
# ===================AIPASS====================
# META DATA HEADER
# Name: get_closed_plans.py - Get Closed Plans Handler
# Date: 2025-11-21
# Version: 1.0.0
# Category: flow/handlers/plan
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2025-11-21): Initial handler - get list of closed plans
#
# CODE STANDARDS:
#   - Handler: Pure logic, no logging, no Prax imports
#   - Returns data structures for module orchestration
# =============================================

"""
Get Closed Plans Handler

Returns list of closed plans from registry.

Usage:
    from aipass.flow.apps.handlers.plan.get_closed_plans import get_closed_plans
    closed_plans = get_closed_plans()
"""

from pathlib import Path
from typing import List, Tuple, Dict, Any

# INFRASTRUCTURE IMPORT PATTERN
_PKG_ROOT = Path(__file__).resolve().parents[4]

# Internal: Registry handler
from aipass.flow.apps.handlers.registry.load_registry import load_registry

# =============================================
# HANDLER FUNCTION
# =============================================

def get_closed_plans() -> List[Tuple[str, Dict[str, Any]]]:
    """
    Get all closed plans from registry

    Returns:
        List of tuples: [(plan_num, plan_info), ...]
        Empty list if no closed plans found

    Example:
        >>> plans = get_closed_plans()
        >>> for plan_num, plan_info in plans:
        ...     print(f"PLAN{plan_num}: {plan_info['subject']}")
    """
    # Load registry
    registry = load_registry()

    # Filter for closed plans
    closed_plans = [
        (plan_num, plan_info)
        for plan_num, plan_info in registry.get("plans", {}).items()
        if plan_info.get("status") == "closed"
    ]

    return closed_plans
