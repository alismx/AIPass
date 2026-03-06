#!/home/aipass/.venv/bin/python3

"""
Dashboard Handlers Package

Provides dashboard write-through for PRAX-managed sections.
"""

from .agent_status_writer import push_agent_status_dashboard

__all__ = ['push_agent_status_dashboard']
