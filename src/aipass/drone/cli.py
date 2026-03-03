"""
Drone CLI — command-line interface for aipass.drone.

Entry point: `drone` (wired via pyproject.toml console_scripts to cli.main).

Usage:
  drone                          Show available commands
  drone --help                   Show help
  drone --version                Show version
  drone systems                  List registered branches
  drone @branch command [args]   Route command to branch
  drone @branch --help           Show help for branch

Zero external dependencies — stdlib only (sys).
"""

from __future__ import annotations

import sys

import aipass
from aipass.drone import (
    CommandExecutionError,
    BranchNotFoundError,
    get_help,
    list_branches,
    route_command,
)

_HELP_TEXT = """\
drone — AIPass branch command router

Usage:
  drone                          Show this help
  drone --help                   Show this help
  drone --version                Show version
  drone systems                  List registered branches
  drone @branch command [args]   Route command to branch
  drone @branch --help           Show help for branch

Examples:
  drone systems
  drone @flow status
  drone @flow run --verbose
  drone @flow --help
"""


def main() -> None:
    """Entry point for the `drone` CLI command.

    Parses sys.argv manually and dispatches to the appropriate handler.
    Exits with the command's exit code on branch commands, 0 on success,
    1 on error.
    """
    args = sys.argv[1:]

    # No args or explicit --help
    if not args or args == ["--help"]:
        print(_HELP_TEXT, end="")
        sys.exit(0)

    # --version
    if args == ["--version"]:
        print(aipass.__version__)
        sys.exit(0)

    # systems — list registered branches
    if args[0] == "systems":
        _cmd_systems()
        return

    # @branch ... — route to a branch
    if args[0].startswith("@"):
        _cmd_branch(args)
        return

    # Unknown command
    print(f"drone: unknown command '{args[0]}'", file=sys.stderr)
    print("Run 'drone --help' for usage.", file=sys.stderr)
    sys.exit(1)


def _cmd_systems() -> None:
    """Handle `drone systems` — list registered branches."""
    branches = list_branches()
    if not branches:
        print("No branches registered.")
        sys.exit(0)

    print(f"Registered branches ({len(branches)}):")
    for name in sorted(branches):
        print(f"  {name}")
    sys.exit(0)


def _cmd_branch(args: list[str]) -> None:
    """Handle `drone @branch command [args]` or `drone @branch --help`."""
    target = args[0]
    rest = args[1:]

    # drone @branch --help
    if not rest or rest == ["--help"]:
        try:
            result = get_help(target)
            if result.text:
                print(result.text, end="")
            else:
                print(f"No help available for {target}.")
        except BranchNotFoundError as exc:
            print(f"drone: {exc}", file=sys.stderr)
            sys.exit(1)
        except CommandExecutionError as exc:
            print(f"drone: {exc}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    # drone @branch command [args...]
    command = rest[0]
    cmd_args = rest[1:]

    try:
        result = route_command(target, command, args=cmd_args if cmd_args else None)
    except BranchNotFoundError as exc:
        print(f"drone: {exc}", file=sys.stderr)
        sys.exit(1)
    except CommandExecutionError as exc:
        print(f"drone: {exc}", file=sys.stderr)
        sys.exit(1)

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    sys.exit(result.exit_code)
