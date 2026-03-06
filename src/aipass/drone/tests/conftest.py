#!/home/aipass/.venv/bin/python3
"""Shared pytest fixtures for drone tests."""

import json
import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_test_dir() -> Generator[Path, None, None]:
    """Creates temporary directory for testing, cleans up after."""
    test_dir = Path(tempfile.mkdtemp())
    yield test_dir
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture
def sample_registry(temp_test_dir: Path) -> Path:
    """Create a sample AIPASS_REGISTRY.json for testing."""
    registry = {
        "metadata": {"version": "1.0.0"},
        "branches": [
            {
                "name": "TEST_BRANCH",
                "path": str(temp_test_dir / "test_branch"),
                "profile": "library",
                "description": "Test branch",
                "email": "@test_branch",
                "status": "active",
            }
        ],
    }
    registry_path = temp_test_dir / "AIPASS_REGISTRY.json"
    registry_path.write_text(json.dumps(registry, indent=2))
    return registry_path
