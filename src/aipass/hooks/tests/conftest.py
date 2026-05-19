# =================== AIPass ====================
# Name: conftest.py
# Version: 1.0.0
# Description: Shared pytest fixtures for hooks tests
# Branch: hooks
# Layer: tests
# Created: 2026-05-18
# Modified: 2026-05-18
# =============================================

"""Shared pytest fixtures for hooks tests."""

import json
import shutil
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pytest


@pytest.fixture
def temp_test_dir() -> Generator[Path, None, None]:
    """Creates temporary directory for testing, cleans up after."""
    test_dir = Path(tempfile.mkdtemp())
    yield test_dir
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture
def sample_hooks_config() -> dict:
    """Minimal hooks.json config for testing."""
    return {
        "hooks_enabled": True,
        "UserPromptSubmit": {
            "test_hook": {
                "enabled": True,
                "command": "echo 'test output'",
                "matcher": "",
            }
        },
        "PreToolUse": {
            "matcher_hook": {
                "enabled": True,
                "command": "echo 'matched'",
                "matcher": "Edit|Write",
            },
            "disabled_hook": {
                "enabled": False,
                "command": "echo 'should not fire'",
                "matcher": "",
            },
        },
    }


@pytest.fixture
def hooks_config_file(temp_test_dir: Path, sample_hooks_config: dict) -> Path:
    """Creates a .aipass/hooks.json in temp dir."""
    config_dir = temp_test_dir / ".aipass"
    config_dir.mkdir()
    config_file = config_dir / "hooks.json"
    config_file.write_text(json.dumps(sample_hooks_config), encoding="utf-8")
    return config_file


@pytest.fixture
def mock_logger():
    """Mock the prax system logger."""
    with patch("aipass.hooks.apps.modules.engine.logger") as mock:
        yield mock


@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run for hook execution tests."""
    with patch("aipass.hooks.apps.modules.engine.subprocess.run") as mock:
        yield mock
