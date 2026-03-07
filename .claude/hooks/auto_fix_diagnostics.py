#!/usr/bin/env python3
"""
Silent Auto-fix Hook - Runs validation and tells Claude to fix silently.

Runs real linters (ruff, py_compile), validates JSON, checks Python patterns.
Outputs via additionalContext so Claude sees errors and fixes them without
announcing.

Version: 1.0.0
"""

import json
import sys
import subprocess
from pathlib import Path

EDIT_TOOLS = ["Edit", "Write", "MultiEdit", "NotebookEdit"]
LAST_FILE_PATH = Path(__file__).parent / ".last_diagnostics_file"
SKIP_EXTENSIONS = {".md", ".txt", ".log", ".csv", ".html"}

PYTHON_PATTERNS = {
    "bad_optional": {
        "pattern": ": str = None",
        "message": "Optional param should use 'str | None = None' pattern",
    },
    "open_no_encoding": {
        "pattern": "open(",
        "requires_missing": "encoding=",
        "message": "open() without encoding='utf-8'",
    },
}

JSON_CORRUPTION_CHARS = ["\ufffd", "\x00"]


def run_python_checks(file_path: str) -> list[str]:
    """Run actual Python validation."""
    errors = []

    try:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", file_path],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            errors.append(f"SYNTAX: {result.stderr.strip()}")
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["ruff", "check", "--select=E,F,W", "--output-format=text", file_path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.stdout.strip():
            for line in result.stdout.strip().split("\n")[:5]:
                errors.append(f"LINT: {line}")
    except FileNotFoundError:
        pass
    except Exception:
        pass

    try:
        content = Path(file_path).read_text(encoding="utf-8")
        for check in PYTHON_PATTERNS.values():
            pattern = check["pattern"]
            message = check["message"]
            requires_missing = check.get("requires_missing")

            if requires_missing:
                if pattern in content and requires_missing not in content:
                    errors.append(f"PATTERN: {message}")
                continue

            for line in content.split("\n"):
                stripped = line.strip()
                if stripped.startswith(("#", '"', "'")):
                    continue
                if f'"{pattern}' in line or f"'{pattern}" in line:
                    continue
                if pattern in line:
                    errors.append(f"PATTERN: {message}")
                    break
    except Exception:
        pass

    return errors


def run_json_checks(file_path: str) -> list[str]:
    """Run actual JSON validation."""
    errors = []

    try:
        content = Path(file_path).read_text(encoding="utf-8")

        for char in JSON_CORRUPTION_CHARS:
            if char in content:
                errors.append(
                    f"CORRUPTION: Found corrupted character '{repr(char)}'"
                )
                break

        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            errors.append(f"JSON SYNTAX: {e.msg} at line {e.lineno}")

    except Exception as e:
        errors.append(f"READ ERROR: {e!s}")

    return errors


def should_skip_file(file_path: str) -> bool:
    """Check if file should be skipped."""
    if not file_path:
        return True
    ext = Path(file_path).suffix.lower()
    return ext in SKIP_EXTENSIONS


def is_same_file_as_last(file_path: str) -> bool:
    """Smart batching - skip if same file as last check."""
    try:
        if LAST_FILE_PATH.exists():
            last = LAST_FILE_PATH.read_text(encoding="utf-8").strip()
            if last == file_path:
                return True
        LAST_FILE_PATH.write_text(file_path, encoding="utf-8")
    except Exception:
        pass
    return False


def main():
    """Main hook entry point."""
    try:
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")

        if tool_name not in EDIT_TOOLS:
            return

        if should_skip_file(file_path):
            return

        if is_same_file_as_last(file_path):
            return

        errors = []
        file_type = ""

        if file_path.endswith(".py"):
            file_type = "Python"
            errors = run_python_checks(file_path)
        elif file_path.endswith(".json"):
            file_type = "JSON"
            errors = run_json_checks(file_path)
        else:
            return

        if errors:
            error_text = "\n".join(f"  - {e}" for e in errors)
            context = f"""[SILENT-FIX] {file_type} errors in {Path(file_path).name}:
{error_text}

Fix these issues silently. Do not announce or explain fixes - just fix and continue."""

            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": context,
                },
                "systemMessage": f"[diagnostics] {len(errors)} issue(s)",
            }
            print(json.dumps(output))
        else:
            output = {"systemMessage": "[diagnostics] ok"}
            print(json.dumps(output))

    except Exception:
        pass


if __name__ == "__main__":
    main()
