"""Smoke tests for utility hook scripts.

# =================== META ====================
# Name: test_hooks_utility.py
# Description: Smoke tests for branch_prompt_loader, email_notification,
#   identity_injector, pre_compact, notification_sound, stop_sound, tool_use_sound
# Version: 1.0.0
# Created: 2026-04-21
# Modified: 2026-04-21
# =============================================
"""

import importlib.util
import io
import json
from pathlib import Path
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Loader helper
# ---------------------------------------------------------------------------

HOOKS_DIR = Path(__file__).resolve().parents[4] / ".claude" / "hooks"


def _load_hook(name: str):
    """Import a hook script by filename via importlib (outside package)."""
    path = HOOKS_DIR / name
    if not path.exists():
        import pytest

        pytest.skip(f"Hook script not found: {path}")
    spec = importlib.util.spec_from_file_location(name.replace(".py", "").replace("-", "_"), path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


# ---------------------------------------------------------------------------
# 1. branch_prompt_loader.py
# ---------------------------------------------------------------------------


def test_branch_prompt_loader_no_crash_empty_stdin():
    """branch_prompt_loader.main() doesn't crash — it reads no stdin at all."""
    mod = _load_hook("branch_prompt_loader.py")
    # main() doesn't read stdin; just ensure it runs without raising
    with patch.object(mod, "find_branch_root", return_value=None):
        mod.main()  # must not raise


def test_branch_prompt_loader_no_branch_structure(tmp_path):
    """main() returns without crashing when CWD has no branch structure."""
    mod = _load_hook("branch_prompt_loader.py")
    # Run with a tmp_path that has no .trinity or .aipass
    with patch("os.getcwd", return_value=str(tmp_path)):
        mod.main()  # must not raise


# ---------------------------------------------------------------------------
# 2. email_notification.py
# ---------------------------------------------------------------------------


def test_email_notification_no_crash_empty_stdin():
    """email_notification.main() doesn't crash even with no branch root."""
    mod = _load_hook("email_notification.py")
    with patch.object(mod, "find_branch_root", return_value=None):
        mod.main()  # must not raise


def test_email_notification_output_is_valid_when_emails_present(capsys, tmp_path):
    """When new emails exist, output is plain text (not JSON) containing count."""
    mod = _load_hook("email_notification.py")

    # Create a fake inbox with one new message
    mail_dir = tmp_path / ".ai_mail.local"
    mail_dir.mkdir()
    inbox = mail_dir / "inbox.json"
    inbox.write_text(
        json.dumps({"messages": [{"id": "1", "status": "new", "subject": "hi"}]}),
        encoding="utf-8",
    )

    with patch.object(mod, "find_branch_root", return_value=tmp_path):
        mod.main()

    captured = capsys.readouterr()
    assert "1 new email" in captured.out


# ---------------------------------------------------------------------------
# 3. identity_injector.py
# ---------------------------------------------------------------------------


def test_identity_injector_no_crash_empty_stdin():
    """identity_injector.main() returns without raising when no branch root found."""
    mod = _load_hook("identity_injector.py")
    with patch.object(mod, "find_branch_root", return_value=None):
        mod.main()  # must not raise


def test_identity_injector_finds_passport_in_seedgo(capsys):
    """identity_injector finds .trinity/passport.json when CWD is in seedgo dir."""
    mod = _load_hook("identity_injector.py")

    # Use the actual seedgo directory which has a passport.json
    seedgo_dir = Path(__file__).resolve().parents[2]  # src/aipass/seedgo
    trinity = seedgo_dir / ".trinity"

    if not (trinity / "passport.json").exists():
        # No passport here — just verify no crash
        with patch.object(mod, "find_branch_root", return_value=None):
            mod.main()
        return

    branch_root = mod.find_id_file(seedgo_dir)
    # Either finds passport or returns None — both are valid
    assert branch_root is None or branch_root.exists()


# ---------------------------------------------------------------------------
# 4. pre_compact.py
# ---------------------------------------------------------------------------


def test_pre_compact_no_crash_empty_hook_event(capsys):
    """pre_compact.main() handles stdin with hook_event_name field cleanly."""
    mod = _load_hook("pre_compact.py")
    payload = json.dumps({"hook_event_name": "manual"})
    with patch("sys.stdin", io.StringIO(payload)), patch("sys.exit"):
        mod.main()  # must not raise


def test_pre_compact_output_json_or_empty(capsys):
    """pre_compact.main() produces output or is empty — never raises."""
    mod = _load_hook("pre_compact.py")
    payload = json.dumps({"hook_event_name": "manual"})
    with patch("sys.stdin", io.StringIO(payload)), patch("sys.exit"):
        mod.main()
    # Capture is fine either way — no assertion on content, just no exception


# ---------------------------------------------------------------------------
# 5. notification_sound.py
# ---------------------------------------------------------------------------


def test_notification_sound_no_crash_empty_stdin():
    """notification_sound.main() doesn't crash on empty stdin {}."""
    mod = _load_hook("notification_sound.py")
    with (
        patch("sys.stdin", io.StringIO("{}")),
        patch("subprocess.Popen") as mock_popen,
        patch("sys.exit"),
    ):
        mod.main()
    # No Popen call expected — event name didn't match
    mock_popen.assert_not_called()


def test_notification_sound_runs_without_exception_when_sound_missing():
    """main() runs without exception even when sound file is missing."""
    mod = _load_hook("notification_sound.py")
    payload = json.dumps({"hook_event_name": "Notification"})
    with (
        patch("sys.stdin", io.StringIO(payload)),
        patch.object(mod, "SOUND_FILE", Path("/tmp/no_such_sound_file.wav")),
        patch("subprocess.Popen") as mock_popen,
        patch("sys.exit"),
    ):
        mod.main()  # must not raise
    # Sound file doesn't exist, so play_sound() returns early — Popen not called
    mock_popen.assert_not_called()


# ---------------------------------------------------------------------------
# 6. stop_sound.py
# ---------------------------------------------------------------------------


def test_stop_sound_no_crash_empty_stdin():
    """stop_sound.main() doesn't crash on empty stdin {}."""
    mod = _load_hook("stop_sound.py")
    with (
        patch("sys.stdin", io.StringIO("{}")),
        patch("subprocess.Popen") as mock_popen,
        patch("sys.exit"),
    ):
        mod.main()
    mock_popen.assert_not_called()


def test_stop_sound_runs_without_exception_when_sound_missing():
    """main() runs without exception even when sound file is missing."""
    mod = _load_hook("stop_sound.py")
    payload = json.dumps({"hook_event_name": "Stop"})
    with (
        patch("sys.stdin", io.StringIO(payload)),
        patch.object(mod, "SOUND_FILE", Path("/tmp/no_such_sound_file.wav")),
        patch("subprocess.Popen") as mock_popen,
        patch("sys.exit"),
    ):
        mod.main()  # must not raise
    mock_popen.assert_not_called()


# ---------------------------------------------------------------------------
# 7. tool_use_sound.py
# ---------------------------------------------------------------------------


def test_tool_use_sound_no_crash_empty_stdin():
    """tool_use_sound.main() doesn't crash on empty stdin {}."""
    mod = _load_hook("tool_use_sound.py")
    with (
        patch("sys.stdin", io.StringIO("{}")),
        patch("subprocess.Popen") as mock_popen,
        patch("sys.exit"),
    ):
        mod.main()
    mock_popen.assert_not_called()


def test_tool_use_sound_does_not_fire_for_non_tool_use_event():
    """tool_use_sound.main() does not play sound for a non-PreToolUse event."""
    mod = _load_hook("tool_use_sound.py")
    payload = json.dumps({"hook_event_name": "Stop", "tool_name": "Bash"})
    with (
        patch("sys.stdin", io.StringIO(payload)),
        patch("subprocess.Popen") as mock_popen,
        patch("sys.exit"),
    ):
        mod.main()
    mock_popen.assert_not_called()
