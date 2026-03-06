
# ===================AIPASS====================
# META DATA HEADER
# Name: telegram_relay.py - Telegram Relay for Mission Control
# Date: 2026-02-18
# Version: 1.0.0
# Category: prax/handlers/monitoring
#
# CHANGELOG (Max 5 entries):
#   - v1.1.0 (2026-03-03): Separated from scheduler bot
#     * Now uses dedicated prax_monitor_config.json (aipass_prax_monitor_bot)
#   - v1.0.0 (2026-02-18): Initial implementation
#     * Buffers monitor events and sends to Telegram scheduler bot
#     * 5-second batch interval, silent notifications
#     * Same urllib pattern as daemon.py (no cross-branch imports)
#     * 4096-char Telegram limit handled via message splitting
#
# CODE STANDARDS:
#   - Handlers implement logic, modules orchestrate
#   - No cross-branch imports
#   - Self-contained: reads config directly, uses urllib
# =============================================

"""
Telegram relay for Mission Control events.

Buffers monitoring events and sends them to the dedicated Prax Monitor Telegram bot
in batches every 5 seconds. Uses silent notifications (disable_notification=True).

Architecture:
    monitor_module.py calls queue_event() for each displayed event.
    A background flush thread sends batched events to Telegram.
    Start/stop lifecycle tied to monitor start/stop.

Usage (from monitor_module.py):
    from aipass.prax.apps.handlers.monitoring.telegram_relay import (
        telegram_start, telegram_stop, telegram_queue_event
    )
    telegram_start()                              # When monitor starts
    telegram_queue_event('file', 'PRAX', '...')   # Each displayed event
    telegram_stop()                               # When monitor stops
"""

from pathlib import Path

# Standard library
import json
import threading
from collections import deque
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError


# =============================================
# CONSTANTS
# =============================================

def _find_repo_root() -> Path:
    """Walk up from this file to find the repo root (contains AIPASS_REGISTRY.json)."""
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "AIPASS_REGISTRY.json").exists():
            return parent
    return Path.cwd()

def _get_prax_monitor_config() -> Path:
    """Lazily resolve prax monitor config path."""
    return _find_repo_root() / ".aipass" / "prax_monitor_config.json"
BATCH_INTERVAL = 5.0  # Seconds between flushes
TELEGRAM_MAX_LENGTH = 4000  # Leave margin under 4096 limit

# =============================================
# MODULE STATE (mutable runtime state, not constants)
# =============================================

_buffer = deque(maxlen=200)
_lock = threading.Lock()
_relay_active = False
_relay_flush_thread = None

# =============================================
# PUBLIC API
# =============================================


def telegram_start():
    """Start the Telegram relay. Call when monitor starts."""
    global _relay_active, _relay_flush_thread
    _relay_active = True
    _relay_flush_thread = threading.Thread(target=_flush_worker, daemon=True)
    _relay_flush_thread.start()
    _send_telegram("🟢 Mission Control monitoring started")
    print("[telegram_relay] Started")


def telegram_stop():
    """Stop the Telegram relay. Call when monitor stops."""
    global _relay_active
    _flush()  # Send remaining buffered events
    _send_telegram("🔴 Mission Control monitoring stopped")
    _relay_active = False
    print("[telegram_relay] Stopped")


def telegram_queue_event(event_type, branch, message, caller=None, target=None):
    """
    Queue a monitoring event for Telegram delivery.

    Args:
        event_type: Event type (file, command, agent, log)
        branch: Branch name
        message: Event message (plain text, no Rich markup)
        caller: Caller branch for command events
        target: Target branch for command events
    """
    timestamp = datetime.now().strftime("%H:%M:%S")

    if event_type == 'command':
        # Format command separator
        parts = []
        if caller and caller.upper() != 'UNKNOWN':
            parts.append(caller)
        if target:
            if parts:
                parts.append(f"→ {target}")
            else:
                parts.append(f"→ {target}")
        context = " ".join(parts)
        if context:
            line = f"─── {context}: {message} ───"
        else:
            line = f"─── {branch}: {message} ───"
    else:
        line = f"{timestamp} [{branch}] {message}"

    with _lock:
        _buffer.append(line)


# =============================================
# INTERNAL
# =============================================


def _flush_worker():
    """Background thread: flush buffer every BATCH_INTERVAL seconds."""
    while _relay_active:
        threading.Event().wait(BATCH_INTERVAL)
        if _relay_active:  # Check again after wait
            _flush()


def _flush():
    """Send all buffered events as one or more Telegram messages."""
    with _lock:
        if not _buffer:
            return
        lines = list(_buffer)
        _buffer.clear()

    text = "\n".join(lines)

    # Split if exceeding Telegram limit
    if len(text) <= TELEGRAM_MAX_LENGTH:
        _send_telegram(text)
    else:
        # Split at line boundaries
        chunk = []
        chunk_len = 0
        for line in lines:
            if chunk_len + len(line) + 1 > TELEGRAM_MAX_LENGTH:
                _send_telegram("\n".join(chunk))
                chunk = []
                chunk_len = 0
            chunk.append(line)
            chunk_len += len(line) + 1
        if chunk:
            _send_telegram("\n".join(chunk))


def _send_telegram(message):
    """Send a message to Telegram via the Prax Monitor bot. Silent failure."""
    try:
        with open(_get_prax_monitor_config(), "r", encoding="utf-8") as f:
            config = json.load(f)
        bot_token = config["telegram_bot_token"]
        chat_id = config["telegram_chat_id"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        print("[telegram_relay] Config not found, skipping")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "disable_notification": True
    }).encode("utf-8")
    req = Request(url, data=payload, headers={"Content-Type": "application/json"})

    try:
        with urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False)
    except (URLError, Exception):
        print("[telegram_relay] Send failed: %s", message[:60])
        return False
