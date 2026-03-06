"""
Seedgo drone adapter — bridges drone routing to seedgo commands.

Drone discovers this module via aipass.drone.modules._MODULE_REGISTRY
and routes `drone @seedgo <command> [args]` here.
"""

import sys
from io import StringIO

DRONE_MODULE = {
    "name": "seedgo",
    "version": "1.0.0",
    "description": "Standards compliance through pluggable standard packs",
}


def handle_command(command: str, args: list[str] | None = None) -> dict:
    """Route a drone command to seedgo's entry point.

    Captures stdout/stderr and returns as dict for drone CLI to print.
    """
    if args is None:
        args = []

    # Build argv as if `seedgo <command> [args]` was called
    original_argv = sys.argv
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    captured_out = StringIO()
    captured_err = StringIO()

    try:
        sys.argv = ["seedgo", command] + args
        sys.stdout = captured_out
        sys.stderr = captured_err

        # Import here to avoid circular imports at module level
        from aipass.seedgo.apps.seedgo import main
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
    """Return help text for seedgo."""
    if command:
        result = handle_command(command, ["--help"])
        return result.get("stdout", "") or result.get("stderr", "")

    return (
        "seedgo — Standards compliance platform\n"
        "\n"
        "Commands:\n"
        "  audit <pack>            Run pack audit against current project\n"
        "  checklist <pack> <file> Check single file against pack standards\n"
        "  list                    Show installed standard packs\n"
        "  verify                  Self-check seedgo installation\n"
        "\n"
        "Usage via drone:\n"
        "  drone @seedgo audit aipass\n"
        "  drone @seedgo list\n"
        "  drone @seedgo verify\n"
    )


def get_introspective() -> str:
    """Discovery mode: show what seedgo has connected."""
    try:
        from aipass.seedgo.apps.seedgo import discover_packs
        packs = discover_packs()
        pack_names = ", ".join(packs.keys()) if packs else "none"
        return (
            f"@seedgo — Standards compliance platform\n"
            f"  Installed packs: {pack_names}\n"
            f"  Run 'drone @seedgo --help' for usage\n"
        )
    except Exception:
        return "@seedgo — Standards compliance platform (run 'drone @seedgo --help' for usage)\n"
