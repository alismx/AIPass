"""
Module and command discovery for AIPass branch introspection.

Introspects branch capabilities by querying entry points for help text
and scanning module directories as a fallback.
"""

import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from aipass.drone.apps.handlers.exceptions import CommandExecutionError
from .resolver import list_branches, resolve_branch

logger = logging.getLogger(__name__)


@dataclass
class HelpResult:
    """Structured result from a help query."""

    branch: str
    command: Optional[str]
    text: str
    commands_found: List[str] = field(default_factory=list)


def _get_entry_point(branch_path: str, branch_name: str) -> Optional[Path]:
    """Return the apps/{branch_name}.py entry point path if it exists."""
    entry_point = Path(branch_path) / "apps" / f"{branch_name}.py"
    return entry_point if entry_point.exists() else None


def _scan_modules_directory(branch_path: str) -> List[str]:
    """Scan apps/modules/ for .py files and return their stems as command names."""
    modules_dir = Path(branch_path) / "apps" / "modules"
    if not modules_dir.is_dir():
        return []

    excluded = {"__init__", "__main__"}
    return sorted(
        f.stem
        for f in modules_dir.glob("*.py")
        if f.stem not in excluded
    )


def _parse_help_for_commands(help_text: str) -> List[str]:
    """Parse --help output to extract a list of available commands."""
    commands: List[str] = []
    in_commands_section = False
    section_markers = {"commands", "subcommands", "available commands"}

    for line in help_text.splitlines():
        stripped = line.strip()

        if any(marker in stripped.lower() for marker in section_markers):
            in_commands_section = True
            continue

        if in_commands_section and not stripped:
            in_commands_section = False
            continue

        if in_commands_section:
            if line.startswith((" ", "\t")) and stripped:
                token = stripped.split()[0]
                if not token.startswith("-"):
                    commands.append(token)

    return commands


def discover_modules(target: str) -> List[str]:
    """Discover available commands for a branch."""
    branch_path = resolve_branch(target)
    branch_name = target.lstrip("@").lower()

    entry_point = _get_entry_point(branch_path, branch_name)
    if entry_point is not None:
        try:
            result = subprocess.run(
                ["python3", str(entry_point.relative_to(branch_path)), "--help"],
                cwd=branch_path,
                capture_output=True,
                timeout=10,
                shell=False,
            )
            help_text = result.stdout.decode("utf-8", errors="replace")
            if not help_text:
                help_text = result.stderr.decode("utf-8", errors="replace")

            commands = _parse_help_for_commands(help_text)
            if commands:
                return commands
        except (subprocess.TimeoutExpired, OSError):
            pass

    return _scan_modules_directory(branch_path)


def get_help(target: str, command: Optional[str] = None) -> HelpResult:
    """Get structured help for a branch or a specific command."""
    branch_path = resolve_branch(target)
    branch_name = target.lstrip("@").lower()

    entry_point = _get_entry_point(branch_path, branch_name)
    if entry_point is None:
        raise CommandExecutionError(
            f"Entry point not found for branch '{branch_name}': "
            f"{Path(branch_path) / 'apps' / (branch_name + '.py')}"
        )

    relative_entry = str(entry_point.relative_to(branch_path))
    if command is None:
        cmd_args = [relative_entry, "--help"]
    else:
        cmd_args = [relative_entry, command, "--help"]

    try:
        result = subprocess.run(
            ["python3"] + cmd_args,
            cwd=branch_path,
            capture_output=True,
            timeout=10,
            shell=False,
        )
    except subprocess.TimeoutExpired as e:
        raise CommandExecutionError(
            f"Help command timed out for branch '{branch_name}'"
        ) from e
    except OSError as e:
        raise CommandExecutionError(
            f"OS error getting help for branch '{branch_name}': {e}"
        ) from e

    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")

    text = stdout if stdout.strip() else stderr
    commands_found = _parse_help_for_commands(text)

    return HelpResult(
        branch=branch_name,
        command=command,
        text=text,
        commands_found=commands_found,
    )


def get_system_help() -> Dict[str, HelpResult]:
    """Aggregate help across all active branches in the registry."""
    results: Dict[str, HelpResult] = {}
    active_branches = list_branches(status="active")

    for symbolic_name in active_branches:
        branch_name = symbolic_name.lstrip("@")
        try:
            help_result = get_help(symbolic_name)
            results[branch_name] = help_result
        except Exception as exc:
            logger.debug(
                "get_system_help: skipping branch '%s': %s",
                branch_name, exc,
            )

    return results
