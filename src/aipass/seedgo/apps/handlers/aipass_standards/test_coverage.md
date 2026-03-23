# Test Coverage Standards
**Status:** Draft v1
**Date:** 2026-03-22

---

## What It Is

The test coverage standard evaluates how well a branch's modules and handlers are exercised by test files. It discovers test files, counts pytest-style test functions, maps which modules they cover via import patterns, and calculates a coverage percentage.

---

## Why It Matters

Untested code is unverified code. Without tests, changes can silently break functionality, regressions go unnoticed, and confidence in the codebase erodes. Test coverage tracking provides visibility into what is tested and what is not, making it clear where investment is needed.

---

## What the Checker Scans For

This is a **branch-level** checker that runs once per branch (not per file). It operates in four phases:

### Phase 1: Discovery

Finds test files by looking in:
- `{branch}/tests/` directory (recursive scan)
- Any file matching `test_*.py` or `*_test.py` elsewhere in the branch

Skips: `__init__.py`, `conftest.py`, `__pycache__`, and directories in the skip list.

### Phase 2: Analysis

For each test file:
- Counts pytest-style test functions (`def test_*` and `async def test_*`)
- Maps tested modules via import patterns:
  - `from aipass.<branch>.apps.modules.<name> import ...`
  - `from aipass.<branch>.apps.handlers.<name> import ...`
  - `import aipass.<branch>.apps.modules.<name>`

### Phase 3: Testable Module Collection

Collects module names from:
- `apps/modules/*.py` -- file stem becomes module name (e.g., `runner.py` -> `runner`)
- `apps/handlers/*.py` -- file stem becomes module name
- `apps/handlers/subdir/` -- directory name if it contains `.py` files

### Phase 4: Coverage Calculation

```
coverage = covered_modules / total_testable_modules * 100
```

Where `covered_modules` is the intersection of tested modules (from imports) and all testable modules.

---

## Three Checks

1. **Test files** -- do any test files exist?
2. **Test functions** -- are there `def test_*` functions?
3. **Module coverage** -- what percentage of modules have test coverage?
   - Threshold: **25%** (lenient -- most branches have no tests yet)

---

## Code Examples

### Violation

A branch with `apps/modules/runner.py` and `apps/handlers/audit/` but no `tests/` directory and no `test_*.py` files anywhere.

### Fix

```python
# tests/test_runner.py
from aipass.seedgo.apps.modules import runner


def test_runner_executes():
    result = runner.run("check")
    assert result is not None


def test_runner_handles_missing_target():
    result = runner.run("")
    assert result["passed"] is False
```

---

## Scoring

- **Scope:** `AUDIT_SCOPE = "branch_level"` -- runs once per branch via `check_branch()`
- **Score formula:** `covered_modules / total_modules * 100`
- **No testable modules:** Score = 100 (nothing to test)
- **Overall pass threshold:** 75%

---

## Skipped Directories

The following directories are excluded from test file discovery:

`__pycache__`, `.archive`, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `.venv`, `venv`, `node_modules`, `.git`, `site-packages`, `logs`, `tools`, `.trinity`, `.aipass`, `.ai_mail.local`, `.spawn`, `backups`, `reports`, `docs`, `.sorting_unprocessed`

---

## Bypass

Bypass rules are configured in `.seedgo/bypass.json`. Supports:

- **Standard-level bypass:** Skip the entire `test_coverage` standard for a branch
- **File-level bypass:** Match by file path substring
- **Line-level bypass:** Skip specific lines (less common for branch-level checks)

Example bypass rule:
```json
{
    "standard": "test_coverage",
    "file": "experimental_branch"
}
```

---

## Reference

- **Checker:** `test_coverage_check.py`
- **Scope:** `branch_level`
- **Entry point:** `check_branch(branch_path, bypass_rules)`
- **Standard label:** `TEST_COVERAGE`
