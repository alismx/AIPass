"""
Trigger package path configuration.

Provides package-relative paths for trigger data directories.
Works in both pip-installed and development environments.
"""

from pathlib import Path

# Trigger package root: .../aipass/trigger/
TRIGGER_ROOT = Path(__file__).resolve().parents[1]

# AIPass package root: .../aipass/
AIPASS_PKG_ROOT = TRIGGER_ROOT.parent
