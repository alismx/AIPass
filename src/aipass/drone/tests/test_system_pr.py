# =================== AIPass ====================
# Name: test_system_pr.py
# Description: Tests for devpulse_ops plugin — auth and system PR workflow
# Version: 1.0.0
# Created: 2026-03-30
# Modified: 2026-04-21
# =============================================

"""Tests for devpulse_ops plugin — auth and system PR workflow."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aipass.drone.apps.plugins.devpulse_ops.auth import (
    ALLOWED_CALLERS,
    verify_caller,
)
from aipass.drone.apps.plugins.devpulse_ops.pr_plugin import (
    create_system_pr,
    slugify,
)


# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture()
def devpulse_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a temp directory with a devpulse passport."""
    trinity = tmp_path / ".trinity"
    trinity.mkdir()
    passport = trinity / "passport.json"
    passport.write_text(
        json.dumps(
            {
                "branch_info": {"branch_name": "devpulse"},
                "identity": {"name": "devpulse"},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture()
def seedgo_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a temp directory with an unauthorized branch passport."""
    trinity = tmp_path / ".trinity"
    trinity.mkdir()
    passport = trinity / "passport.json"
    passport.write_text(
        json.dumps(
            {
                "branch_info": {"branch_name": "citizen/unauthorized"},
                "identity": {"name": "citizen/unauthorized"},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture()
def no_passport_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a temp directory with no passport."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture()
def repo_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a temp repo root with AIPASS_REGISTRY.json."""
    registry = tmp_path / "AIPASS_REGISTRY.json"
    registry.write_text("{}", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path


# ===========================================================================
# Module-level subprocess side-effect helpers
# ===========================================================================

# Responses for "nothing staged" scenario: (stdout, returncode)
_NOTHING_TO_COMMIT_RESPONSES: dict[tuple[str, ...], tuple[str, int]] = {
    ("git", "rev-parse", "--abbrev-ref"): ("main\n", 0),
    ("git", "add", "-u"): ("", 0),
    ("git", "diff", "--cached"): ("", 0),  # exit 0 = nothing staged
    ("git", "fetch", "origin"): ("", 0),
    ("git", "rev-list", "--count"): ("0\n", 0),
}

# Responses for a complete successful PR flow: (stdout, returncode)
_PR_FLOW_RESPONSES: dict[tuple[str, ...], tuple[str, int]] = {
    ("git", "rev-parse", "--abbrev-ref"): ("main\n", 0),
    ("git", "add", "-u"): ("", 0),
    ("git", "diff", "--cached"): ("diff --git a/foo.py b/foo.py\n", 1),  # 1 = staged
    ("git", "fetch", "origin"): ("", 0),
    ("git", "rev-list", "--count"): ("1\n", 0),
    ("git", "commit"): ("[main abc1234] test description\n", 0),
    ("git", "branch"): ("", 0),
    ("git", "push"): ("", 0),
    ("gh", "pr"): ("https://github.com/org/repo/pull/42\n", 0),
}


def _make_proc(stdout: str, returncode: int) -> MagicMock:
    """Build a minimal subprocess mock with stdout, returncode, and empty stderr."""
    proc = MagicMock()
    proc.stdout = stdout
    proc.returncode = returncode
    proc.stderr = ""
    return proc


def _nothing_to_commit_side_effect(cmd: list[str], **kwargs: object) -> MagicMock:
    """Return a mock proc for the 'nothing staged' subprocess sequence."""
    stdout, rc = _NOTHING_TO_COMMIT_RESPONSES.get(tuple(cmd[:3]), ("", 0))
    return _make_proc(stdout, rc)


def _pr_flow_run_side_effect(cmd: list[str], **kwargs: object) -> MagicMock:
    """Return a mock proc for a complete successful PR-flow subprocess sequence."""
    stdout, rc = _PR_FLOW_RESPONSES.get(tuple(cmd[:2]), ("", 0))
    return _make_proc(stdout, rc)


# ===========================================================================
# 1. auth.verify_caller tests
# ===========================================================================


class TestVerifyCallerAuthorized:
    """verify_caller should return the branch name for devpulse."""

    def test_verify_caller_with_devpulse_passport(self, devpulse_dir: Path) -> None:
        """Devpulse passport resolves to the 'devpulse' branch name."""
        result = verify_caller()
        assert result == "devpulse"
        assert result in ALLOWED_CALLERS


class TestVerifyCallerUnauthorized:
    """verify_caller should raise PermissionError for non-devpulse branches."""

    def test_verify_caller_unauthorized(self, seedgo_dir: Path) -> None:
        """An unauthorized branch raises PermissionError with 'not authorized'."""
        with pytest.raises(PermissionError, match="not authorized"):
            verify_caller()

    def test_error_message_includes_branch_name(self, seedgo_dir: Path) -> None:
        """The PermissionError message includes the actual branch name."""
        with pytest.raises(PermissionError, match="citizen/unauthorized"):
            verify_caller()


class TestVerifyCallerNoPassport:
    """verify_caller should raise PermissionError when no passport exists."""

    def test_verify_caller_no_passport(self, no_passport_dir: Path) -> None:
        """Missing passport raises PermissionError mentioning passport path."""
        with pytest.raises(PermissionError, match="No .trinity/passport.json"):
            verify_caller()


# ===========================================================================
# 2. slugify tests
# ===========================================================================


class TestSlugify:
    """Test the slugify function with various inputs."""

    def test_basic_slugify(self) -> None:
        """Space-separated words become hyphen-separated lowercase slugs."""
        assert slugify("Update all configs") == "update-all-configs"

    def test_special_characters_removed(self) -> None:
        """Punctuation and special characters are stripped from the output."""
        assert slugify("fix: broken pipe!") == "fix-broken-pipe"

    def test_multiple_spaces_collapse(self) -> None:
        """Consecutive spaces collapse into a single hyphen."""
        assert slugify("too   many   spaces") == "too-many-spaces"

    def test_max_length_truncation(self) -> None:
        """Slugs longer than 50 characters are truncated."""
        long_desc = "a" * 100
        result = slugify(long_desc)
        assert len(result) <= 50

    def test_leading_trailing_hyphens_stripped(self) -> None:
        """Leading and trailing hyphens are stripped from the result."""
        assert slugify("  --hello world--  ") == "hello-world"

    def test_empty_string(self) -> None:
        """An empty input returns an empty string."""
        assert slugify("") == ""

    def test_all_special_chars(self) -> None:
        """A string of only special characters produces an empty slug."""
        assert slugify("!!!@@@###") == ""

    def test_mixed_case(self) -> None:
        """Mixed-case input is normalized to lowercase."""
        assert slugify("Hello World FOO") == "hello-world-foo"


# ===========================================================================
# 3. create_system_pr — not on main
# ===========================================================================


class TestSystemPrNotOnMain:
    """create_system_pr should fail when not on main branch."""

    @patch("aipass.drone.apps.plugins.devpulse_ops.pr_plugin.find_repo_root")
    @patch("aipass.drone.apps.plugins.devpulse_ops.pr_plugin.subprocess.run")
    def test_system_pr_not_on_main(self, mock_run: MagicMock, mock_root: MagicMock, tmp_path: Path) -> None:
        """Returns failure dict when HEAD is on a feature branch instead of main."""
        mock_root.return_value = tmp_path
        mock_run.return_value = _make_proc("feature/something\n", 0)

        result = create_system_pr("test description", "devpulse")

        assert result["success"] is False
        assert "Not on main branch" in result["message"]


# ===========================================================================
# 4. create_system_pr — nothing to commit
# ===========================================================================


class TestSystemPrNothingToCommit:
    """create_system_pr should fail when there are no changes to PR."""

    @patch("aipass.drone.apps.plugins.devpulse_ops.pr_plugin.release_lock")
    @patch("aipass.drone.apps.plugins.devpulse_ops.pr_plugin.acquire_lock")
    @patch("aipass.drone.apps.plugins.devpulse_ops.pr_plugin.find_repo_root")
    @patch("aipass.drone.apps.plugins.devpulse_ops.pr_plugin.subprocess.run")
    def test_system_pr_nothing_to_commit(
        self,
        mock_run: MagicMock,
        mock_root: MagicMock,
        mock_acquire: MagicMock,
        mock_release: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Returns failure dict with 'Nothing to PR' when no staged changes exist."""
        mock_root.return_value = tmp_path
        mock_acquire.return_value = {"success": True, "message": "Lock acquired"}
        mock_run.side_effect = _nothing_to_commit_side_effect

        result = create_system_pr("test description", "devpulse")

        assert result["success"] is False
        assert "Nothing to PR" in result["message"]


# ===========================================================================
# 5. create_system_pr — HEAD stays on main (no git checkout)
# ===========================================================================


class TestSystemPrHeadStaysOnMain:
    """system-pr must never call 'git checkout' — HEAD stays on main throughout."""

    @patch("aipass.drone.apps.plugins.devpulse_ops.pr_plugin.release_lock")
    @patch("aipass.drone.apps.plugins.devpulse_ops.pr_plugin.acquire_lock")
    @patch("aipass.drone.apps.plugins.devpulse_ops.pr_plugin.find_repo_root")
    @patch("aipass.drone.apps.plugins.devpulse_ops.pr_plugin.subprocess.run")
    def test_no_git_checkout_during_successful_system_pr(
        self,
        mock_run: MagicMock,
        mock_root: MagicMock,
        mock_acquire: MagicMock,
        mock_release: MagicMock,
        tmp_path: Path,
    ) -> None:
        """No subprocess call contains 'git checkout' during a complete PR flow."""
        mock_root.return_value = tmp_path
        mock_acquire.return_value = {"success": True, "message": "Lock acquired"}
        mock_run.side_effect = _pr_flow_run_side_effect

        create_system_pr("test description", "devpulse")

        all_cmds = [c[0][0] if c[0] else c.args[0] for c in mock_run.call_args_list]
        assert not any("checkout" in cmd for cmd in all_cmds)


# ===========================================================================
# 6. git_module routing for system-pr
# ===========================================================================


class TestGitModuleSystemPrRouting:
    """Test that git_module routes system-pr correctly."""

    def test_system_pr_in_commands(self) -> None:
        """The _COMMANDS registry includes the 'system-pr' verb."""
        from aipass.drone.apps.modules.git_module import _COMMANDS

        assert "system-pr" in _COMMANDS

    def test_get_help_includes_system_pr(self) -> None:
        """Generic get_help() output mentions 'system-pr'."""
        from aipass.drone.apps.modules.git_module import get_help

        help_text = get_help()
        assert "system-pr" in help_text

    def test_get_help_system_pr_specific(self) -> None:
        """get_help('system-pr') output mentions deprecation."""
        from aipass.drone.apps.modules.git_module import get_help

        help_text = get_help("system-pr")
        assert "deprecated" in help_text.lower()

    def test_get_introspective_includes_plugin(self) -> None:
        """get_introspective() output mentions the devpulse_ops plugin."""
        from aipass.drone.apps.modules.git_module import get_introspective

        intro = get_introspective()
        assert "devpulse_ops" in intro

    @patch("aipass.drone.apps.plugins.devpulse_ops.auth.verify_git_access", return_value="devpulse")
    def test_handle_system_pr_no_args(self, mock_verify: MagicMock) -> None:
        """handle_command('system-pr', []) exits with code 1 and deprecation message."""
        from aipass.drone.apps.modules.git_module import handle_command

        result = handle_command("system-pr", [])
        assert result["exit_code"] == 1
        assert "deprecated" in result["stderr"].lower()

    @patch(
        "aipass.drone.apps.plugins.devpulse_ops.auth.verify_git_access",
        side_effect=PermissionError("not authorized"),
    )
    def test_handle_system_pr_unauthorized(self, mock_verify: MagicMock) -> None:
        """handle_command propagates PermissionError as exit_code 1 with the message."""
        from aipass.drone.apps.modules.git_module import handle_command

        result = handle_command("system-pr", ["test"])
        assert result["exit_code"] == 1
        assert "not authorized" in result["stderr"]
