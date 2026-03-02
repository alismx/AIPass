"""
Paths module custom exceptions.

Defines the exception hierarchy for path resolution errors.
"""

from __future__ import annotations


class PathResolutionError(Exception):
    """Raised when the AIPass root directory cannot be resolved."""

    pass
