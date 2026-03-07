"""Tests for spawn drone_adapter integration."""

import pytest


def test_drone_module_has_required_keys():
    """DRONE_MODULE dict must have name, version, description."""
    from aipass.spawn.drone_adapter import DRONE_MODULE

    assert "name" in DRONE_MODULE
    assert "version" in DRONE_MODULE
    assert "description" in DRONE_MODULE
    assert DRONE_MODULE["name"] == "spawn"


def test_handle_command_help_returns_output():
    """handle_command('--help', []) should return help text."""
    from aipass.spawn.drone_adapter import handle_command

    result = handle_command("--help", [])
    assert isinstance(result, dict)
    assert "stdout" in result
    assert "stderr" in result
    assert "exit_code" in result
    # Help text goes to stdout (via Rich console)
    output = result["stdout"] + result["stderr"]
    assert len(output) > 0 or result["exit_code"] == 0


def test_handle_command_create_help_no_crash():
    """handle_command('create', ['--help']) should not crash."""
    from aipass.spawn.drone_adapter import handle_command

    result = handle_command("create", ["--help"])
    assert isinstance(result, dict)
    assert "exit_code" in result
    # Should not be an unhandled crash (exit_code 0 or 1 are fine)
    assert isinstance(result["exit_code"], int)


def test_stub_update_not_implemented():
    """Stub command 'update' should return not-yet-implemented message."""
    from aipass.spawn.drone_adapter import handle_command

    result = handle_command("update", [])
    assert isinstance(result, dict)
    # The stub returns exit_code 1
    assert result["exit_code"] == 1


def test_stub_delete_not_implemented():
    """Stub command 'delete' should return not-yet-implemented message."""
    from aipass.spawn.drone_adapter import handle_command

    result = handle_command("delete", [])
    assert isinstance(result, dict)
    assert result["exit_code"] == 1


def test_sync_registry_report():
    """sync-registry with no args should produce a report (exit 0)."""
    from aipass.spawn.drone_adapter import handle_command

    result = handle_command("sync-registry", [])
    assert isinstance(result, dict)
    assert result["exit_code"] == 0


def test_sync_templates_report():
    """sync-templates with no args should produce a status report (exit 0)."""
    from aipass.spawn.drone_adapter import handle_command

    result = handle_command("sync-templates", [])
    assert isinstance(result, dict)
    assert result["exit_code"] == 0


def test_stub_regenerate_registry_not_implemented():
    """Stub command 'regenerate-registry' should return not-yet-implemented message."""
    from aipass.spawn.drone_adapter import handle_command

    result = handle_command("regenerate-registry", [])
    assert isinstance(result, dict)
    assert result["exit_code"] == 1


def test_get_help_returns_all_commands():
    """get_help() should list all commands including stubs."""
    from aipass.spawn.drone_adapter import get_help

    help_text = get_help()
    assert "create" in help_text
    assert "update" in help_text
    assert "delete" in help_text
    assert "sync-registry" in help_text
    assert "sync-templates" in help_text
    assert "regenerate-registry" in help_text


def test_get_introspective_returns_string():
    """get_introspective() should return a non-empty string."""
    from aipass.spawn.drone_adapter import get_introspective

    result = get_introspective()
    assert isinstance(result, str)
    assert "@spawn" in result


def test_module_registry_includes_spawn():
    """spawn should be registered in the drone module registry."""
    from aipass.drone.apps.modules.module_registry import is_module

    assert is_module("spawn")
