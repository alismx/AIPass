"""
Drone CLI — command-line interface for aipass.drone.

Entry point: `drone` (wired via pyproject.toml console_scripts).
Thin wrapper that delegates to apps/drone.py main().

Usage:
  drone                          Show available commands
  drone --help                   Show help
  drone --version                Show version
  drone systems                  List registered branches and modules
  drone @branch command [args]   Route command to branch
  drone @module command [args]   Route command to internal module
"""

import sys

from aipass.drone.apps.drone import main as _drone_main


def main() -> None:
    """Entry point for the `drone` CLI command."""
    sys.exit(_drone_main())


if __name__ == "__main__":
    main()
