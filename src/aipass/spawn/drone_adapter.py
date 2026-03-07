"""
Spawn drone adapter — bridges drone routing to spawn commands.

Drone discovers this module via aipass.drone.modules._MODULE_REGISTRY
and routes `drone @spawn <command> [args]` here.
"""

import sys
from io import StringIO

DRONE_MODULE = {
    "name": "spawn",
    "version": "1.0.0",
    "description": "Agent creation and branch lifecycle management",
}


def handle_command(command: str, args: list[str] | None = None) -> dict:
    """Route a drone command to spawn's entry point.

    Captures stdout/stderr and returns as dict for drone CLI to print.
    """
    if args is None:
        args = []

    # Build argv as if `spawn <command> [args]` was called
    original_argv = sys.argv
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    captured_out = StringIO()
    captured_err = StringIO()

    try:
        sys.argv = ["spawn", command] + args
        sys.stdout = captured_out
        sys.stderr = captured_err

        # Import here to avoid circular imports at module level
        from aipass.spawn.apps.spawn import main
        exit_code = main()
    except SystemExit as e:
        exit_code = e.code if e.code is not None else 0
    except Exception as e:
        captured_err.write(str(e))
        exit_code = 1
    finally:
        sys.argv = original_argv
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    return {
        "stdout": captured_out.getvalue(),
        "stderr": captured_err.getvalue(),
        "exit_code": exit_code if isinstance(exit_code, int) else 1,
    }


def get_help(command: str | None = None) -> str:
    """Return help text for spawn."""
    if command:
        result = handle_command(command, ["--help"])
        return result.get("stdout", "") or result.get("stderr", "")

    return (
        "spawn — Agent creation and branch lifecycle management\n"
        "\n"
        "Commands:\n"
        "  create <path>           Create new branch from template\n"
        "  update <@branch|--all>  Update branch(es) from template  [not yet implemented]\n"
        "  delete <@branch>        Archive and deregister branch     [not yet implemented]\n"
        "  sync-registry           Repair registry against filesystem [not yet implemented]\n"
        "  sync-templates          Pull managed files from source     [not yet implemented]\n"
        "  regenerate-registry     Regenerate template registry hashes [not yet implemented]\n"
        "\n"
        "Usage via drone:\n"
        "  drone @spawn create <target_path> [--role ...] [--traits ...]\n"
        "  drone @spawn update @branch_name\n"
        "  drone @spawn delete @branch_name\n"
        "  drone @spawn sync-registry\n"
        "  drone @spawn --help\n"
    )


def get_introspective() -> str:
    """Discovery mode: show what spawn has available."""
    try:
        from pathlib import Path
        template_dir = Path(__file__).parent / "templates"
        templates = [d.name for d in template_dir.iterdir() if d.is_dir()] if template_dir.exists() else []
        template_list = ", ".join(templates) if templates else "none"
        return (
            f"@spawn — Agent creation and branch lifecycle management\n"
            f"  Templates available: {template_list}\n"
            f"  Run 'drone @spawn --help' for usage\n"
        )
    except Exception:
        return "@spawn — Agent creation and branch lifecycle management (run 'drone @spawn --help' for usage)\n"
