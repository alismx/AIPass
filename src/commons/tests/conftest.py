# ===================AIPASS====================
# META DATA HEADER
# Name: conftest.py - The Commons test configuration
# Date: 2026-03-07
# Version: 1.0.0
# Category: commons/tests
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-03-07): Initial creation (FPLAN-0411)
#
# CODE STANDARDS:
#   - Pytest fixtures for The Commons test suite
#   - Uses temporary database for test isolation
# =============================================

"""
The Commons - Test Configuration

Provides pytest fixtures for database setup, teardown,
and test isolation using temporary databases.
"""

import tempfile
from pathlib import Path

import pytest

try:
    from aipass.prax.apps.modules.logger import system_logger as logger
except ImportError:
    import logging
    logger = logging.getLogger("commons.tests")


@pytest.fixture
def tmp_db_path(tmp_path):
    """
    Provide a temporary database path for test isolation.

    Each test gets its own fresh database file that is
    automatically cleaned up after the test completes.

    Yields:
        Path to temporary database file.
    """
    db_file = tmp_path / "test_commons.db"
    yield db_file


@pytest.fixture
def initialized_db(tmp_db_path):
    """
    Provide an initialized temporary database with schema and seed data.

    Creates a fresh database with all tables, default rooms,
    and room personalities. Closes the connection after the test.

    Yields:
        sqlite3.Connection to the initialized test database.
    """
    from commons.apps.handlers.database.db import init_db, close_db

    conn = init_db(db_path=tmp_db_path)
    yield conn
    close_db(conn)
