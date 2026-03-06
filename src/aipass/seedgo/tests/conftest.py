"""Shared pytest fixtures for seedgo tests"""

# =================== META ====================
# Name: conftest.py
# Description: Shared pytest fixtures for seedgo tests
# Version: 1.0.0
# Created: 2026-03-05
# Modified: 2026-03-05
# =============================================

import pytest
import shutil
import tempfile
from pathlib import Path
from typing import Generator


@pytest.fixture
def temp_test_dir() -> Generator[Path, None, None]:
    """Creates temporary directory for testing, cleans up after"""
    test_dir = Path(tempfile.mkdtemp())
    yield test_dir
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture
def sample_test_data() -> dict:
    """Provides sample test data

    Customize this fixture for your module's needs
    """
    return {
        "test_key": "test_value",
        "sample_data": "example"
    }
