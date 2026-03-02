"""
Tests for aipass.paths — root resolution and derived path functions.

Covers:
    - get_root() env var resolution
    - get_root() marker walk resolution
    - get_root() default fallback
    - Priority order (env var beats marker walk, marker walk beats default)
    - Invalid env var raises PathResolutionError
    - All derived path functions
    - branch_path() with a mock registry
    - branch_path() returns None for missing branch / missing file
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from aipass.paths import (
    PathResolutionError,
    branch_logs_dir,
    branch_path,
    branch_registry_path,
    get_root,
    system_logs_dir,
)
from aipass.paths.resolver import _resolve_from_marker, get_root as _get_root_direct


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_registry(path: Path, branches: dict) -> None:
    """Write a minimal BRANCH_REGISTRY.json to *path*."""
    path.write_text(
        json.dumps({"version": "1.0", "branches": branches}),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# get_root() — environment variable resolution
# ---------------------------------------------------------------------------


class TestEnvVarResolution:
    """Tier 1: AIPASS_ROOT environment variable."""

    def test_env_var_valid_directory_is_returned(self, tmp_path, monkeypatch):
        """When AIPASS_ROOT points to an existing directory it is returned."""
        monkeypatch.setenv("AIPASS_ROOT", str(tmp_path))
        assert get_root() == tmp_path

    def test_env_var_takes_priority_over_marker(self, tmp_path, monkeypatch):
        """Env var wins even when a .aipass/ marker exists in CWD."""
        env_root = tmp_path / "env_root"
        env_root.mkdir()

        marker_root = tmp_path / "marker_root"
        marker_root.mkdir()
        (marker_root / ".aipass").mkdir()

        monkeypatch.setenv("AIPASS_ROOT", str(env_root))
        monkeypatch.chdir(marker_root)

        assert get_root() == env_root

    def test_env_var_nonexistent_raises_path_resolution_error(self, monkeypatch):
        """AIPASS_ROOT pointing to a non-existent path raises PathResolutionError."""
        monkeypatch.setenv("AIPASS_ROOT", "/does/not/exist/at/all")
        with pytest.raises(PathResolutionError):
            get_root()

    def test_env_var_empty_string_falls_through(self, tmp_path, monkeypatch):
        """An empty AIPASS_ROOT string is treated as unset (falls through to next tier)."""
        # Make a marker so tier 2 picks it up (avoids writing to real home)
        marker_root = tmp_path / "marker"
        marker_root.mkdir()
        (marker_root / ".aipass").mkdir()

        monkeypatch.setenv("AIPASS_ROOT", "")
        monkeypatch.chdir(marker_root)

        # Empty string → env var absent → should find marker
        result = get_root()
        assert result == marker_root

    def test_env_var_unset_falls_through(self, tmp_path, monkeypatch):
        """When AIPASS_ROOT is not set at all, env tier returns None and we fall through."""
        monkeypatch.delenv("AIPASS_ROOT", raising=False)

        marker_root = tmp_path / "marker"
        marker_root.mkdir()
        (marker_root / ".aipass").mkdir()
        monkeypatch.chdir(marker_root)

        result = get_root()
        assert result == marker_root


# ---------------------------------------------------------------------------
# get_root() — marker walk resolution
# ---------------------------------------------------------------------------


class TestMarkerWalkResolution:
    """Tier 2: .aipass/ marker directory walk."""

    def test_marker_in_cwd_is_found(self, tmp_path, monkeypatch):
        """A .aipass/ directory in CWD is resolved to CWD."""
        monkeypatch.delenv("AIPASS_ROOT", raising=False)
        (tmp_path / ".aipass").mkdir()
        monkeypatch.chdir(tmp_path)

        assert get_root() == tmp_path

    def test_marker_in_parent_is_found(self, tmp_path, monkeypatch):
        """A .aipass/ in a parent directory is discovered by walking up."""
        monkeypatch.delenv("AIPASS_ROOT", raising=False)

        root = tmp_path / "project"
        root.mkdir()
        (root / ".aipass").mkdir()

        deep = root / "a" / "b" / "c"
        deep.mkdir(parents=True)
        monkeypatch.chdir(deep)

        assert get_root() == root

    def test_marker_in_grandparent_is_found(self, tmp_path, monkeypatch):
        """Walk stops at the nearest ancestor that contains .aipass/."""
        monkeypatch.delenv("AIPASS_ROOT", raising=False)

        grandparent = tmp_path / "gp"
        grandparent.mkdir()
        (grandparent / ".aipass").mkdir()

        child = grandparent / "child" / "grandchild"
        child.mkdir(parents=True)
        monkeypatch.chdir(child)

        assert get_root() == grandparent

    def test_marker_file_not_directory_is_ignored(self, tmp_path, monkeypatch):
        """If .aipass exists but is a file (not dir), it should not match."""
        monkeypatch.delenv("AIPASS_ROOT", raising=False)

        # .aipass as a file, not a directory
        (tmp_path / ".aipass").write_text("not a dir")

        # Provide a parent with the real marker so the walk finds something
        parent = tmp_path.parent
        # We cannot rely on parent having .aipass, so use custom start to
        # test the helper directly
        result = _resolve_from_marker(start=tmp_path)
        # The file should not match; result will be None or a higher ancestor
        # that may or may not have .aipass — what matters is tmp_path itself
        # is NOT returned because .aipass there is a file.
        if result is not None:
            assert result != tmp_path

    def test_explicit_start_directory(self, tmp_path, monkeypatch):
        """_resolve_from_marker accepts an explicit start directory."""
        monkeypatch.delenv("AIPASS_ROOT", raising=False)

        root = tmp_path / "root"
        root.mkdir()
        (root / ".aipass").mkdir()

        start = root / "sub"
        start.mkdir()

        result = _resolve_from_marker(start=start)
        assert result == root

    def test_no_marker_returns_none(self, tmp_path, monkeypatch):
        """_resolve_from_marker returns None when no .aipass/ is found."""
        monkeypatch.delenv("AIPASS_ROOT", raising=False)
        # tmp_path has no .aipass and neither do its parents (almost certainly)
        result = _resolve_from_marker(start=tmp_path)
        # We can only assert it does not match tmp_path itself
        if result is not None:
            assert (result / ".aipass").is_dir()


# ---------------------------------------------------------------------------
# get_root() — default fallback
# ---------------------------------------------------------------------------


class TestDefaultFallback:
    """Tier 3: ~/.aipass/ default fallback."""

    def test_default_fallback_returns_home_aipass(self, tmp_path, monkeypatch):
        """When env var absent and no marker found, default is ~/.aipass/."""
        monkeypatch.delenv("AIPASS_ROOT", raising=False)

        # Use a temp home with no .aipass marker anywhere in the tree
        fake_home = tmp_path / "home" / "user"
        fake_home.mkdir(parents=True)
        monkeypatch.setenv("HOME", str(fake_home))
        # Patch Path.home() by redirecting the env; also chdir to a location
        # with no .aipass marker
        isolated = tmp_path / "isolated"
        isolated.mkdir()
        monkeypatch.chdir(isolated)

        result = get_root()
        expected = Path.home() / ".aipass"
        assert result == expected

    def test_default_fallback_creates_directory(self, tmp_path, monkeypatch):
        """The default fallback creates ~/.aipass/ if it does not exist."""
        monkeypatch.delenv("AIPASS_ROOT", raising=False)

        fake_home = tmp_path / "fresh_home"
        fake_home.mkdir()
        monkeypatch.setenv("HOME", str(fake_home))

        isolated = tmp_path / "isolated2"
        isolated.mkdir()
        monkeypatch.chdir(isolated)

        result = get_root()
        assert result.is_dir()


# ---------------------------------------------------------------------------
# Priority order
# ---------------------------------------------------------------------------


class TestPriorityOrder:
    """Verify env var > marker walk > default."""

    def test_env_var_beats_marker_walk(self, tmp_path, monkeypatch):
        """Env var takes priority over marker walk."""
        env_root = tmp_path / "env"
        env_root.mkdir()

        cwd_with_marker = tmp_path / "cwd"
        cwd_with_marker.mkdir()
        (cwd_with_marker / ".aipass").mkdir()

        monkeypatch.setenv("AIPASS_ROOT", str(env_root))
        monkeypatch.chdir(cwd_with_marker)

        assert get_root() == env_root

    def test_marker_walk_beats_default(self, tmp_path, monkeypatch):
        """Marker walk takes priority over default fallback."""
        monkeypatch.delenv("AIPASS_ROOT", raising=False)

        marker_root = tmp_path / "project"
        marker_root.mkdir()
        (marker_root / ".aipass").mkdir()
        monkeypatch.chdir(marker_root)

        result = get_root()
        assert result == marker_root


# ---------------------------------------------------------------------------
# Derived path functions
# ---------------------------------------------------------------------------


class TestSystemLogsDir:
    def test_returns_system_logs_under_root(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AIPASS_ROOT", str(tmp_path))
        assert system_logs_dir() == tmp_path / "system_logs"

    def test_returns_path_object(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AIPASS_ROOT", str(tmp_path))
        assert isinstance(system_logs_dir(), Path)


class TestBranchRegistryPath:
    def test_returns_registry_under_root(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AIPASS_ROOT", str(tmp_path))
        assert branch_registry_path() == tmp_path / "BRANCH_REGISTRY.json"

    def test_returns_path_object(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AIPASS_ROOT", str(tmp_path))
        assert isinstance(branch_registry_path(), Path)


class TestBranchPath:
    """branch_path(name) reads BRANCH_REGISTRY.json and returns a Path or None."""

    def test_known_branch_returns_path(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AIPASS_ROOT", str(tmp_path))
        _write_registry(
            tmp_path / "BRANCH_REGISTRY.json",
            {"vera": {"name": "vera", "path": "/home/aipass/vera", "type": "agent", "status": "active"}},
        )
        result = branch_path("vera")
        assert result == Path("/home/aipass/vera")

    def test_unknown_branch_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AIPASS_ROOT", str(tmp_path))
        _write_registry(tmp_path / "BRANCH_REGISTRY.json", {})
        assert branch_path("nonexistent") is None

    def test_missing_registry_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AIPASS_ROOT", str(tmp_path))
        # No registry file written
        assert branch_path("vera") is None

    def test_corrupt_registry_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AIPASS_ROOT", str(tmp_path))
        (tmp_path / "BRANCH_REGISTRY.json").write_text("not valid json {{{{", encoding="utf-8")
        assert branch_path("vera") is None

    def test_branch_entry_missing_path_key_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AIPASS_ROOT", str(tmp_path))
        _write_registry(
            tmp_path / "BRANCH_REGISTRY.json",
            {"vera": {"name": "vera", "type": "agent"}},  # no "path" key
        )
        assert branch_path("vera") is None

    def test_returns_path_object(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AIPASS_ROOT", str(tmp_path))
        branch_dir = tmp_path / "branches" / "flow"
        branch_dir.mkdir(parents=True)
        _write_registry(
            tmp_path / "BRANCH_REGISTRY.json",
            {"flow": {"name": "flow", "path": str(branch_dir), "type": "agent", "status": "active"}},
        )
        result = branch_path("flow")
        assert isinstance(result, Path)
        assert result == branch_dir

    def test_multiple_branches_correct_one_returned(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AIPASS_ROOT", str(tmp_path))
        _write_registry(
            tmp_path / "BRANCH_REGISTRY.json",
            {
                "alpha": {"name": "alpha", "path": "/agents/alpha", "type": "agent", "status": "active"},
                "beta": {"name": "beta", "path": "/agents/beta", "type": "agent", "status": "active"},
            },
        )
        assert branch_path("alpha") == Path("/agents/alpha")
        assert branch_path("beta") == Path("/agents/beta")
        assert branch_path("gamma") is None


class TestBranchLogsDir:
    def test_returns_logs_under_branch_dir(self, tmp_path):
        result = branch_logs_dir(tmp_path)
        assert result == tmp_path / "logs"

    def test_returns_path_object(self, tmp_path):
        assert isinstance(branch_logs_dir(tmp_path), Path)

    def test_arbitrary_path(self):
        p = Path("/some/branch/dir")
        assert branch_logs_dir(p) == Path("/some/branch/dir/logs")


# ---------------------------------------------------------------------------
# PathResolutionError
# ---------------------------------------------------------------------------


class TestPathResolutionError:
    def test_is_exception_subclass(self):
        assert issubclass(PathResolutionError, Exception)

    def test_carries_message(self):
        err = PathResolutionError("bad path")
        assert "bad path" in str(err)

    def test_raised_on_invalid_env_var(self, monkeypatch):
        monkeypatch.setenv("AIPASS_ROOT", "/totally/nonexistent/12345")
        with pytest.raises(PathResolutionError, match="AIPASS_ROOT"):
            get_root()
