# =================== AIPass ====================
# Name: test_coverage_content.py
# Description: Test Coverage Standards Content Handler
# Version: 1.0.0
# Created: 2026-03-22
# Modified: 2026-03-22
# =============================================

"""
Test Coverage Standards Content Handler

Provides formatted Test Coverage standards content.
Module orchestrates, handler implements.
"""

from aipass.seedgo.apps.handlers.json import json_handler


def get_test_coverage_standards() -> str:
    """Return formatted test_coverage standards content with Rich markup

    Returns:
        str: Formatted standards text with Rich styling
    """
    lines = [
        "[bold cyan]CORE PRINCIPLE:[/bold cyan]",
        "  Every branch should have tests. Test coverage measures how many",
        "  of a branch's modules and handlers are exercised by test files.",
        "  Untested code is unverified code.",
        "",
        "[bold cyan]WHAT IT CHECKS:[/bold cyan]",
        "  Branch-level analysis in four phases:",
        "",
        "  [yellow]Phase 1 -- Discovery:[/yellow]",
        "  Finds test files in [dim]tests/[/dim] directory (recursive) and",
        "  scattered [dim]test_*.py[/dim] / [dim]*_test.py[/dim] files elsewhere",
        "  Skips: __init__.py, conftest.py, __pycache__",
        "",
        "  [yellow]Phase 2 -- Analysis:[/yellow]",
        "  Counts pytest-style test functions ([dim]def test_*[/dim] and",
        "  [dim]async def test_*[/dim]) in each test file",
        "  Maps tested modules via import patterns:",
        "  [dim]from aipass.<branch>.apps.modules.<name> import ...[/dim]",
        "  [dim]from aipass.<branch>.apps.handlers.<name> import ...[/dim]",
        "",
        "  [yellow]Phase 3 -- Testable modules:[/yellow]",
        "  Collects module names from [dim]apps/modules/*.py[/dim] and",
        "  [dim]apps/handlers/*.py[/dim] (or subdirectories with .py files)",
        "",
        "  [yellow]Phase 4 -- Coverage calculation:[/yellow]",
        "  [dim]coverage = covered_modules / total_testable_modules * 100[/dim]",
        "",
        "[bold cyan]THREE CHECKS:[/bold cyan]",
        "",
        "  [bold]1. Test files[/bold] -- do any test files exist?",
        "  [bold]2. Test functions[/bold] -- are there [dim]def test_*[/dim] functions?",
        "  [bold]3. Module coverage[/bold] -- what % of modules are covered?",
        "     Threshold: [yellow]25%[/yellow] (lenient -- most branches have no tests yet)",
        "",
        "[bold cyan]VIOLATIONS:[/bold cyan]",
        "",
        "  [red]Fail:[/red] No [dim]tests/[/dim] directory and no test_*.py files found",
        "  [red]Fail:[/red] Test files exist but contain no [dim]def test_*[/dim] functions",
        "  [red]Fail:[/red] Module coverage below 25% threshold",
        "",
        "[bold cyan]HOW TO FIX:[/bold cyan]",
        "",
        "  1. Create a [dim]tests/[/dim] directory in your branch",
        "  2. Add test files with pytest-style test functions:",
        "",
        "  [green]Good:[/green]",
        "  [dim]# tests/test_runner.py[/dim]",
        "  [dim]from aipass.seedgo.apps.modules import runner[/dim]",
        "  [dim][/dim]",
        "  [dim]def test_runner_executes():[/dim]",
        "  [dim]    result = runner.run(\"check\")[/dim]",
        "  [dim]    assert result is not None[/dim]",
        "",
        "  3. Import the modules you are testing so the coverage mapper",
        "     can detect which modules your tests cover",
        "",
        "[yellow]SCOPE:[/yellow]",
        "  AUDIT_SCOPE = [bold]branch_level[/bold]",
        "  Runs once per branch (not per file). Entry point: [dim]check_branch()[/dim]",
        "",
        "[bold cyan]SCORING:[/bold cyan]",
        "  Score = [dim]covered_modules / total_modules * 100[/dim]",
        "  If branch has 0 testable modules: score = [green]100[/green]",
        "  Overall pass threshold: [yellow]75%[/yellow]",
        "",
        "[bold cyan]BYPASS:[/bold cyan]",
        "  Via [dim].seedgo/bypass.json[/dim] -- supports standard-level and",
        "  file-level bypass rules",
        "",
        "[bold cyan]SKIPPED DIRECTORIES:[/bold cyan]",
        "  __pycache__, .archive, .mypy_cache, .ruff_cache, .pytest_cache,",
        "  .venv, venv, node_modules, .git, site-packages, logs, tools,",
        "  .trinity, .aipass, .ai_mail.local, .spawn, backups, reports, docs",
        "",
        "[bold cyan]REFERENCE:[/bold cyan]",
        "  [dim]See: seedgo standards pack (test_coverage)[/dim]",
        "  [dim]Checker: test_coverage_check.py[/dim]",
    ]

    json_handler.log_operation("standard_content_queried", {"standard": "test_coverage"})
    return "\n".join(lines)
