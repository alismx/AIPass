
# ===================AIPASS====================
# META DATA HEADER
# Name: telegram_command_bot.py - Telegram Command Bot for Prax Monitor
# Date: 2026-02-23
# Version: 1.0.0
# Category: prax/handlers/monitoring
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-02-23): Initial implementation
#     * Polls scheduler bot for commands (10s interval)
#     * /prax_on - Start headless file/log monitoring with Telegram relay
#     * /prax_off - Stop monitoring
#     * /status - System health report (daemon, VERA, PRs, errors)
#     * Runs as long-lived background process
#
# CODE STANDARDS:
#   - No cross-branch imports (standalone)
#   - Uses urllib (same pattern as daemon.py)
#   - Silent Telegram failures (non-blocking)
# =============================================

"""
Telegram Command Bot for Prax Monitor

Polls the scheduler bot for commands from Patrick. Enables phone-based
control of Prax monitoring and system status checks.

Commands:
    /prax_on   - Start monitoring (file changes + daemon log → Telegram)
    /prax_off  - Stop monitoring
    /status    - System health snapshot
    /help      - Show available commands

Usage:
    # Start as background process
    nohup python3 telegram_command_bot.py &

    # Or run directly
    python3 telegram_command_bot.py

Architecture:
    Long-running poller → reads Telegram updates → dispatches commands
    Monitoring runs in background threads when active.
"""

from pathlib import Path

import json
import os
import signal
import subprocess
import threading
import time
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError

from aipass.prax.apps.modules.logger import get_direct_logger

logger = get_direct_logger()

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

_repo_root_cache: Path | None = None

def _get_repo_root() -> Path:
    """Lazily resolve repo root."""
    global _repo_root_cache
    if _repo_root_cache is None:
        _repo_root_cache = _find_repo_root()
    return _repo_root_cache

def _get_config_path() -> Path:
    return _get_repo_root() / ".aipass" / "scheduler_config.json"

def _get_daemon_log() -> Path:
    return _get_repo_root() / "src" / "aipass" / "ai_mail" / "ai_mail.local" / "dispatch_daemon.log"

def _get_vera_notepad() -> Path:
    return _get_repo_root() / "src" / "aipass" / "vera" / "NOTEPAD.md"

def _get_monitor_pid_file() -> Path:
    return _get_repo_root() / ".aipass" / "prax_monitor.pid"
POLL_INTERVAL = 10  # seconds
TELEGRAM_MAX_LENGTH = 4000
PATRICK_CHAT_ID = "7235222625"

# =============================================
# MODULE STATE
# =============================================

_running = True
_monitoring_active = False
_monitor_thread = None
_last_update_id = 0
_last_log_pos = 0


# =============================================
# TELEGRAM API
# =============================================


def _load_config():
    """Load scheduler bot config."""
    try:
        with open(_get_config_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.warning("Config not found")
        return None


def _send_message(text, config=None):
    """Send a message to Patrick via scheduler bot."""
    if config is None:
        config = _load_config()
    if not config:
        return False

    url = f"https://api.telegram.org/bot{config['telegram_bot_token']}/sendMessage"
    payload = json.dumps({
        "chat_id": config.get("telegram_chat_id", PATRICK_CHAT_ID),
        "text": text[:TELEGRAM_MAX_LENGTH],
        "parse_mode": "HTML",
        "disable_notification": False
    }).encode("utf-8")
    req = Request(url, data=payload, headers={"Content-Type": "application/json"})

    try:
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read()).get("ok", False)
    except (URLError, Exception) as e:
        logger.warning("Send failed: %s", e)
        return False


def _get_updates(config, offset=0):
    """Poll for new messages."""
    url = (
        f"https://api.telegram.org/bot{config['telegram_bot_token']}"
        f"/getUpdates?offset={offset}&timeout=5&allowed_updates=[\"message\"]"
    )
    try:
        with urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read())
            if data.get("ok"):
                return data.get("result", [])
    except (URLError, Exception) as e:
        logger.warning("Poll failed: %s", e)
    return []


# =============================================
# MONITORING
# =============================================


def _monitor_daemon_log():
    """Background thread: tail daemon log and relay important events."""
    global _last_log_pos, _monitoring_active

    config = _load_config()
    if not config:
        return

    _send_message("🟢 <b>Prax Monitor ON</b>\nWatching daemon log for events.", config)

    try:
        if _get_daemon_log().exists():
            _last_log_pos = _get_daemon_log().stat().st_size
    except OSError:
        _last_log_pos = 0

    while _monitoring_active:
        try:
            if _get_daemon_log().exists():
                current_size = _get_daemon_log().stat().st_size
                if current_size > _last_log_pos:
                    with open(_get_daemon_log(), "r", encoding="utf-8") as f:
                        f.seek(_last_log_pos)
                        new_lines = f.readlines()
                    _last_log_pos = current_size

                    # Filter for important events
                    important = []
                    for line in new_lines:
                        line = line.strip()
                        if any(kw in line for kw in ["SPAWN", "ERROR", "STOPPED", "STARTED", "error", "failed"]):
                            important.append(line)

                    if important:
                        text = "\n".join(important[-10:])  # Last 10 important lines
                        _send_message(f"📡 <b>Daemon Activity</b>\n<pre>{text}</pre>", config)

        except Exception as e:
            logger.warning("Monitor error: %s", e)

        time.sleep(15)  # Check every 15 seconds


def _start_monitoring():
    """Start Prax monitoring."""
    global _monitoring_active, _monitor_thread

    if _monitoring_active:
        return "Already monitoring."

    _monitoring_active = True
    _monitor_thread = threading.Thread(target=_monitor_daemon_log, daemon=True)
    _monitor_thread.start()

    # Write PID file
    try:
        _get_monitor_pid_file().write_text(str(os.getpid()))
    except OSError:
        pass

    return "Prax monitoring started. Watching daemon log."


def _stop_monitoring():
    """Stop Prax monitoring."""
    global _monitoring_active

    if not _monitoring_active:
        return "Not currently monitoring."

    _monitoring_active = False
    config = _load_config()
    _send_message("🔴 <b>Prax Monitor OFF</b>", config)

    # Remove PID file
    try:
        _get_monitor_pid_file().unlink(missing_ok=True)
    except OSError:
        pass

    return "Prax monitoring stopped."


# =============================================
# COMMANDS
# =============================================


def _cmd_status():
    """Generate system status report."""
    lines = ["📊 <b>AIPass System Status</b>", ""]

    # Daemon check
    try:
        result = subprocess.run(
            ["pgrep", "-f", "daemon.py"],
            capture_output=True, text=True, timeout=5
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split("\n")
            lines.append(f"✅ Daemon: Running (PID {pids[0]})")
        else:
            lines.append("❌ Daemon: NOT running")
    except Exception:
        lines.append("⚠️ Daemon: Check failed")

    # VERA check - last NOTEPAD entry
    try:
        with open(_get_vera_notepad(), "r", encoding="utf-8") as f:
            content = f.read()
        # Find first "What Just Happened" line
        for line in content.split("\n"):
            if "What Just Happened" in line:
                session = line.strip().replace("### ", "")
                lines.append(f"🤖 VERA: {session}")
                break
    except Exception:
        lines.append("⚠️ VERA: Could not read NOTEPAD")

    # PR check
    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--repo", "AIOSAI/AIPass", "--state", "open", "--json", "number,title"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            prs = json.loads(result.stdout)
            if prs:
                lines.append(f"📋 Open PRs: {len(prs)}")
                for pr in prs[:3]:
                    lines.append(f"  • #{pr['number']}: {pr['title'][:40]}")
            else:
                lines.append("📋 Open PRs: 0")
    except Exception:
        lines.append("⚠️ PRs: Check failed")

    # Monitor status
    if _monitoring_active:
        lines.append("📡 Prax Monitor: ON")
    else:
        lines.append("📡 Prax Monitor: OFF")

    # Timestamp
    lines.append(f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    return "\n".join(lines)


def _cmd_help():
    """Show available commands."""
    return (
        "🤖 <b>AIPass Prax Bot</b>\n\n"
        "/prax_on — Start monitoring (daemon events → Telegram)\n"
        "/prax_off — Stop monitoring\n"
        "/status — System health check\n"
        "/help — This message"
    )


def _handle_command(text, config):
    """Route command to handler."""
    text = text.strip().lower()

    if text in ("/prax_on", "/praxon", "/monitor_on", "/start"):
        result = _start_monitoring()
        _send_message(f"🟢 {result}", config)

    elif text in ("/prax_off", "/praxoff", "/monitor_off", "/stop"):
        result = _stop_monitoring()
        _send_message(f"🔴 {result}", config)

    elif text in ("/status", "/s"):
        result = _cmd_status()
        _send_message(result, config)

    elif text in ("/help", "/h"):
        result = _cmd_help()
        _send_message(result, config)

    else:
        # Ignore non-commands
        pass


# =============================================
# MAIN LOOP
# =============================================


def _signal_handler(sig, frame):
    """Handle shutdown signals."""
    global _running, _monitoring_active
    logger.info("Received signal %s, shutting down...", sig)
    _monitoring_active = False
    _running = False


def main():
    """Main polling loop."""
    global _running, _last_update_id

    signal.signal(signal.SIGTERM, _signal_handler)
    signal.signal(signal.SIGINT, _signal_handler)

    config = _load_config()
    if not config:
        logger.warning("No config found. Exiting.")
        return

    logger.info("Prax Command Bot started. Polling every %ss.", POLL_INTERVAL)
    _send_message("🤖 <b>Prax Command Bot started</b>\nType /help for commands.", config)

    # Get latest update_id to skip old messages
    updates = _get_updates(config, offset=0)
    if updates:
        _last_update_id = updates[-1]["update_id"] + 1

    while _running:
        updates = _get_updates(config, offset=_last_update_id)

        for update in updates:
            _last_update_id = update["update_id"] + 1
            msg = update.get("message", {})
            text = msg.get("text", "")
            chat_id = str(msg.get("chat", {}).get("id", ""))

            # Only respond to Patrick
            if chat_id == PATRICK_CHAT_ID and text.startswith("/"):
                logger.info("Command: %s", text)
                _handle_command(text, config)

        time.sleep(POLL_INTERVAL)

    # Cleanup
    _stop_monitoring()
    _get_monitor_pid_file().unlink(missing_ok=True)
    logger.info("Prax Command Bot stopped.")


if __name__ == "__main__":
    main()
