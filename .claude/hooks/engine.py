# =================== AIPass ====================
# Name: engine.py
# Description: Hook Engine — unified dispatcher for all hook events
# Version: 0.3.0
# Created: 2026-05-17
# Modified: 2026-05-17
# =============================================

"""
Hook Engine — DPLAN-0184 Phase 1.

Single entry point for all hook events. Reads per-project config (.aipass/hooks.json),
dispatches to registered hooks, logs everything via prax logger.

Called from provider settings (must use venv python for prax imports):
    $AIPASS_HOME/.venv/bin/python3 $AIPASS_HOME/.claude/hooks/engine.py <EventType>

Stdin/stdout contract matches the platform's hook interface.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

from aipass.prax.apps.modules.logger import system_logger as logger

AIPASS_HOME = os.environ.get("AIPASS_HOME", "")
LOG_DIR = Path(AIPASS_HOME) / ".claude" / "hooks" if AIPASS_HOME else Path(__file__).parent
LOG_FILE = LOG_DIR / "engine.jsonl"


def _find_project_config() -> dict | None:
    """Walk up from CWD looking for .aipass/hooks.json."""
    search = Path.cwd()
    home = Path.home()
    while search != home and search.parent != search:
        config = search / ".aipass" / "hooks.json"
        if config.exists():
            try:
                raw = config.read_text(encoding="utf-8")
                if AIPASS_HOME:
                    raw = raw.replace("$AIPASS_HOME", AIPASS_HOME)
                return json.loads(raw)
            except (json.JSONDecodeError, OSError) as exc:
                logger.error("[hook_engine] bad config %s: %s", config, exc)
                return None
        search = search.parent
    return None


def _log(entry: dict) -> None:
    """Append a JSONL log entry for detailed diagnostics."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as exc:
        logger.error("[hook_engine] log write failed: %s", exc)


def _run_hook(hook_cmd: str, stdin_data: str) -> dict:
    """Run a single hook subprocess, capture output and timing."""
    env = os.environ.copy()
    start = time.monotonic()
    try:
        result = subprocess.run(
            hook_cmd,
            shell=True,
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        elapsed_ms = (time.monotonic() - start) * 1000
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "elapsed_ms": round(elapsed_ms, 1),
        }
    except subprocess.TimeoutExpired:
        elapsed_ms = (time.monotonic() - start) * 1000
        logger.error("[hook_engine] timeout after 30s: %s", hook_cmd)
        return {"exit_code": -1, "stdout": "", "stderr": "TIMEOUT", "elapsed_ms": round(elapsed_ms, 1)}
    except OSError as exc:
        elapsed_ms = (time.monotonic() - start) * 1000
        logger.error("[hook_engine] exec error: %s: %s", hook_cmd, exc)
        return {"exit_code": -1, "stdout": "", "stderr": str(exc), "elapsed_ms": round(elapsed_ms, 1)}


def _matches(matcher: str, value: str) -> bool:
    """Check if a hook's matcher string matches the given value."""
    if not matcher:
        return True
    return value in matcher.split("|")


def dispatch(event_type: str, stdin_data: str, config: dict) -> str:
    """Core dispatch — run hooks for event, return merged stdout."""
    if not config.get("hooks_enabled", True):
        logger.info("[hook_engine] all hooks disabled")
        _log({"ts": time.time(), "event": event_type, "action": "all_hooks_disabled"})
        return ""

    event_hooks = config.get(event_type, {})
    if not event_hooks:
        _log({"ts": time.time(), "event": event_type, "action": "no_hooks_configured"})
        return ""

    match_value = ""
    try:
        parsed = json.loads(stdin_data) if stdin_data.strip() else {}
        match_value = parsed.get("tool_name", "") or parsed.get("compact_type", "") or parsed.get("type", "")
    except json.JSONDecodeError as exc:
        logger.warning("[hook_engine] stdin parse error: %s", exc)

    outputs = []
    total_start = time.monotonic()

    for hook_name, hook_def in event_hooks.items():
        if not hook_def.get("enabled", True):
            logger.info("[hook_engine] %s.%s skipped (disabled)", event_type, hook_name)
            _log({"ts": time.time(), "event": event_type, "hook": hook_name, "action": "skipped_disabled"})
            continue

        command = hook_def.get("command", "")
        matcher = hook_def.get("matcher", "")
        if not command:
            continue

        if matcher and not _matches(matcher, match_value):
            _log({"ts": time.time(), "event": event_type, "hook": hook_name, "action": "skipped_no_match",
                  "matcher": matcher, "value": match_value})
            continue

        result = _run_hook(command, stdin_data)

        logger.info(
            "[hook_engine] %s.%s exit=%d out=%db %dms",
            event_type, hook_name, result["exit_code"],
            len(result["stdout"]), result["elapsed_ms"],
        )
        _log({
            "ts": time.time(),
            "event": event_type,
            "hook": hook_name,
            "exit_code": result["exit_code"],
            "elapsed_ms": result["elapsed_ms"],
            "stdout_len": len(result["stdout"]),
            "stderr_preview": result["stderr"][:200] if result["stderr"] else "",
            "cwd": str(Path.cwd()),
        })

        if result["exit_code"] == 2:
            is_intentional_block = False
            try:
                decision = json.loads(result["stdout"]) if result["stdout"].strip() else {}
                is_intentional_block = decision.get("decision") == "block"
            except (json.JSONDecodeError, AttributeError):
                pass

            if is_intentional_block:
                total_ms = (time.monotonic() - total_start) * 1000
                logger.warning(
                    "[hook_engine] %s BLOCKED by %s (%dms)",
                    event_type, hook_name, total_ms,
                )
                _log({"ts": time.time(), "event": event_type, "action": "blocked",
                      "hook": hook_name, "total_ms": round(total_ms, 1)})
                return result["stdout"]

            logger.error(
                "[hook_engine] %s.%s CRASHED exit=2: %s",
                event_type, hook_name, result["stderr"][:200],
            )
            _log({"ts": time.time(), "event": event_type, "hook": hook_name,
                  "action": "crashed", "stderr": result["stderr"][:200]})

        if result["stdout"]:
            outputs.append(result["stdout"])

    total_ms = (time.monotonic() - total_start) * 1000
    logger.info("[hook_engine] %s complete: %d hooks %dms", event_type, len(outputs), total_ms)
    _log({"ts": time.time(), "event": event_type, "action": "complete",
          "hooks_run": len(outputs), "total_ms": round(total_ms, 1)})

    return "\n".join(outputs)


def main() -> None:
    """Entry point — receive event type, dispatch, output result."""
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: engine.py <EventType>\n")
        sys.exit(1)

    event_type = sys.argv[1]

    stdin_data = ""
    if not sys.stdin.isatty():
        stdin_data = sys.stdin.read()

    config = _find_project_config()
    if config is None:
        config = {"hooks_enabled": True}

    output = dispatch(event_type, stdin_data, config)
    if output:
        sys.stdout.write(output)


if __name__ == "__main__":
    main()
