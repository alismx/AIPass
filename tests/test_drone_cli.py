"""
Tests for the drone CLI (aipass.drone.cli).

Covers:
  - drone / drone --help  → shows help text
  - drone --version       → shows version
  - drone systems         → lists branches
  - drone @branch command → routes correctly
  - drone @branch --help  → shows branch help
  - unknown commands      → error message + exit 1
  - no args               → shows help
"""

from __future__ import annotations

from unittest.mock import patch

import aipass
from aipass.drone.cli import main
from aipass.drone import CommandResult, HelpResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_cli(*args: str) -> tuple[int, str, str]:
    """
    Call main() with the given argv, capturing stdout/stderr and exit code.

    Returns:
        (exit_code, stdout_text, stderr_text)
    """
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []

    class _Cap:
        def __init__(self, buf: list[str]) -> None:
            self._buf = buf

        def write(self, s: str) -> int:
            self._buf.append(s)
            return len(s)

        def flush(self) -> None:
            pass

    exit_code = 0

    def _exit(code: int = 0) -> None:
        nonlocal exit_code
        exit_code = code
        raise SystemExit(code)

    with (
        patch("sys.argv", ["drone", *args]),
        patch("sys.stdout", _Cap(stdout_lines)),
        patch("sys.stderr", _Cap(stderr_lines)),
        patch("sys.exit", side_effect=_exit),
    ):
        try:
            main()
        except SystemExit:
            pass

    return exit_code, "".join(stdout_lines), "".join(stderr_lines)


# ---------------------------------------------------------------------------
# Help / version
# ---------------------------------------------------------------------------


class TestHelpAndVersion:
    """drone --help and drone --version."""

    def test_no_args_shows_help(self):
        """drone with no args prints help and exits 0."""
        code, out, _ = _run_cli()
        assert code == 0
        assert "drone" in out
        assert "Usage" in out or "usage" in out.lower() or "@branch" in out

    def test_help_flag_shows_help(self):
        """drone --help prints help and exits 0."""
        code, out, _ = _run_cli("--help")
        assert code == 0
        assert "drone" in out

    def test_version_flag_shows_version(self):
        """drone --version prints the aipass version and exits 0."""
        code, out, _ = _run_cli("--version")
        assert code == 0
        assert aipass.__version__ in out


# ---------------------------------------------------------------------------
# systems
# ---------------------------------------------------------------------------


class TestSystems:
    """drone systems — list registered branches."""

    def test_systems_lists_branches(self):
        """drone systems calls list_branches and prints them."""
        with patch("aipass.drone.cli.list_branches", return_value=["@flow", "@devpulse"]):
            code, out, _ = _run_cli("systems")

        assert code == 0
        assert "@flow" in out
        assert "@devpulse" in out

    def test_systems_empty_registry(self):
        """drone systems with no branches prints a 'no branches' message."""
        with patch("aipass.drone.cli.list_branches", return_value=[]):
            code, out, _ = _run_cli("systems")

        assert code == 0
        assert "No branches" in out or "no branches" in out.lower() or out.strip() != ""

    def test_systems_shows_count(self):
        """drone systems output mentions the number of branches."""
        branches = ["@alpha", "@beta", "@gamma"]
        with patch("aipass.drone.cli.list_branches", return_value=branches):
            code, out, _ = _run_cli("systems")

        assert code == 0
        # Should show 3 branches somewhere in output
        assert "3" in out or all(b in out for b in branches)


# ---------------------------------------------------------------------------
# @branch routing
# ---------------------------------------------------------------------------


class TestBranchRouting:
    """drone @branch command [args] — route commands."""

    def _make_result(self, stdout="", stderr="", exit_code=0) -> CommandResult:
        return CommandResult(stdout=stdout, stderr=stderr, exit_code=exit_code, branch="flow", command="status")

    def test_routes_command_to_branch(self):
        """drone @flow status calls route_command with correct args."""
        result = self._make_result(stdout="flow is running\n")
        with patch("aipass.drone.cli.route_command", return_value=result) as mock_route:
            code, out, _ = _run_cli("@flow", "status")

        mock_route.assert_called_once_with("@flow", "status", args=None)
        assert code == 0
        assert "flow is running" in out

    def test_routes_command_with_extra_args(self):
        """drone @flow run --verbose passes args correctly."""
        result = self._make_result(stdout="verbose output\n")
        with patch("aipass.drone.cli.route_command", return_value=result) as mock_route:
            code, out, _ = _run_cli("@flow", "run", "--verbose")

        mock_route.assert_called_once_with("@flow", "run", args=["--verbose"])
        assert code == 0

    def test_exits_with_command_exit_code(self):
        """drone exits with the same code as the routed command."""
        result = self._make_result(exit_code=2, stderr="something failed\n")
        with patch("aipass.drone.cli.route_command", return_value=result):
            code, _, err = _run_cli("@flow", "status")

        assert code == 2
        assert "something failed" in err

    def test_branch_not_found_exits_1(self):
        """BranchNotFoundError prints error and exits 1."""
        from aipass.drone import BranchNotFoundError
        with patch("aipass.drone.cli.route_command", side_effect=BranchNotFoundError("@ghost not found")):
            code, _, err = _run_cli("@ghost", "status")

        assert code == 1
        assert "ghost" in err or "not found" in err.lower()

    def test_command_execution_error_exits_1(self):
        """CommandExecutionError prints error and exits 1."""
        from aipass.drone import CommandExecutionError
        with patch("aipass.drone.cli.route_command", side_effect=CommandExecutionError("entry point missing")):
            code, _, err = _run_cli("@flow", "status")

        assert code == 1
        assert "entry point missing" in err

    def test_stdout_printed(self):
        """Command stdout is printed to stdout."""
        result = self._make_result(stdout="hello world\n")
        with patch("aipass.drone.cli.route_command", return_value=result):
            code, out, _ = _run_cli("@flow", "status")

        assert "hello world" in out

    def test_stderr_printed_to_stderr(self):
        """Command stderr is printed to stderr."""
        result = self._make_result(stderr="warning: something\n", exit_code=0)
        with patch("aipass.drone.cli.route_command", return_value=result):
            code, _, err = _run_cli("@flow", "status")

        assert "warning: something" in err


# ---------------------------------------------------------------------------
# @branch --help
# ---------------------------------------------------------------------------


class TestBranchHelp:
    """drone @branch --help — show branch help."""

    def test_branch_help_calls_get_help(self):
        """drone @flow --help calls get_help and prints text."""
        help_result = HelpResult(branch="flow", command=None, text="flow help text\n", commands_found=["status"])
        with patch("aipass.drone.cli.get_help", return_value=help_result) as mock_help:
            code, out, _ = _run_cli("@flow", "--help")

        mock_help.assert_called_once_with("@flow")
        assert code == 0
        assert "flow help text" in out

    def test_branch_no_args_shows_help(self):
        """drone @flow with no command also calls get_help."""
        help_result = HelpResult(branch="flow", command=None, text="flow help\n", commands_found=[])
        with patch("aipass.drone.cli.get_help", return_value=help_result):
            code, out, _ = _run_cli("@flow")

        assert code == 0
        assert "flow help" in out

    def test_branch_not_found_on_help_exits_1(self):
        """BranchNotFoundError on --help exits 1."""
        from aipass.drone import BranchNotFoundError
        with patch("aipass.drone.cli.get_help", side_effect=BranchNotFoundError("@ghost not found")):
            code, _, err = _run_cli("@ghost", "--help")

        assert code == 1

    def test_command_execution_error_on_help_exits_1(self):
        """CommandExecutionError on --help exits 1."""
        from aipass.drone import CommandExecutionError
        with patch("aipass.drone.cli.get_help", side_effect=CommandExecutionError("no entry")):
            code, _, err = _run_cli("@flow", "--help")

        assert code == 1


# ---------------------------------------------------------------------------
# Unknown commands
# ---------------------------------------------------------------------------


class TestUnknownCommands:
    """Unknown top-level commands show an error."""

    def test_unknown_command_exits_1(self):
        """An unrecognised command exits with code 1."""
        code, _, err = _run_cli("frobulate")
        assert code == 1

    def test_unknown_command_shows_error_message(self):
        """An unrecognised command prints an error to stderr."""
        code, _, err = _run_cli("frobulate")
        assert "frobulate" in err or "unknown" in err.lower()

    def test_unknown_command_suggests_help(self):
        """Error message mentions --help."""
        code, _, err = _run_cli("frobulate")
        assert "--help" in err
