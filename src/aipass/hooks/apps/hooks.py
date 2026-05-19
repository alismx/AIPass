# =================== AIPass ====================
# Name: hooks.py
# Version: 1.0.0
# Description: Hook infrastructure — drone entry point
# Branch: hooks
# Layer: apps
# Created: 2026-05-18
# Modified: 2026-05-18
# =============================================

"""
HOOKS Branch — Hook infrastructure for AIPass.

Owns all hook dispatch via engine.py. Platform bridges (Claude, Codex, Gemini)
call the engine, which reads per-project config and routes to handlers.
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("AIPASS_BRANCH_NAME", "hooks")

from aipass.prax.apps.modules.logger import system_logger as logger  # noqa: E402


def print_help() -> None:
    """Print hook system help."""
    logger.info("[HOOKS] help requested")
    sys.stdout.write(
        "HOOKS - Hook infrastructure for AIPass\n"
        "\n"
        "USAGE:\n"
        "  drone @hooks status        Show hook config for current project\n"
        "  drone @hooks log           Tail recent hook activity\n"
        "  drone @hooks test          Run hook test suite\n"
        "  drone @hooks --help        This help\n"
        "  drone @hooks --version     Version info\n"
        "\n"
        "MODULES:\n"
        "  engine       Core dispatch — routes events to handlers via config\n"
        "\n"
        "BRIDGES:\n"
        "  claude       Claude Code bridge (provider settings entry point)\n"
        "  codex        Codex bridge (planned)\n"
        "  gemini       Gemini bridge (planned)\n"
    )


def print_introspection() -> dict:
    """Return branch introspection data for drone discovery."""
    return {
        "branch": "hooks",
        "role": "hook_infrastructure",
        "commands": ["status", "log", "test"],
        "modules": ["engine"],
        "bridges": ["claude"],
    }


def handle_command(command: str, args: list) -> bool:
    """Route commands to appropriate handler."""
    if command == "status":
        from aipass.hooks.apps.modules.engine import find_project_config

        config = find_project_config()
        if config is None:
            sys.stdout.write("No .aipass/hooks.json found for current project\n")
        else:
            enabled = config.get("hooks_enabled", True)
            sys.stdout.write(f"Hooks enabled: {enabled}\n")
            for event_type, hooks in config.items():
                if event_type.startswith("_") or event_type == "hooks_enabled":
                    continue
                if isinstance(hooks, dict):
                    active = sum(1 for h in hooks.values() if isinstance(h, dict) and h.get("enabled", True))
                    total = sum(1 for h in hooks.values() if isinstance(h, dict))
                    sys.stdout.write(f"  {event_type}: {active}/{total} hooks active\n")
        return True

    if command == "log":
        log_file = Path(__file__).resolve().parent.parent / "logs" / "engine.jsonl"
        if not log_file.exists():
            sys.stdout.write("No engine log found\n")
        else:
            lines = log_file.read_text().strip().split("\n")
            for line in lines[-20:]:
                sys.stdout.write(line + "\n")
        return True

    return False


def main() -> int:
    """Main entry point — routes commands or shows help."""
    args = sys.argv[1:]

    if not args:
        data = print_introspection()
        sys.stdout.write(f"HOOKS — {data['role']}\n")
        sys.stdout.write(f"  Modules: {', '.join(data['modules'])}\n")
        sys.stdout.write(f"  Bridges: {', '.join(data['bridges'])}\n")
        sys.stdout.write(f"  Commands: {', '.join(data['commands'])}\n")
        return 0

    if args[0] in ("--help", "-h", "help"):
        print_help()
        return 0

    if args[0] in ("--version", "-V"):
        sys.stdout.write("hooks 1.0.0\n")
        return 0

    command = args[0]
    remaining = args[1:] if len(args) > 1 else []

    if handle_command(command, remaining):
        return 0

    sys.stdout.write(f"Unknown command: {command}. Try: drone @hooks --help\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
