#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: notifier.py - Telegram Push Notifications
# Date: 2026-02-17
# Version: 1.1.0
# Category: api/handlers/telegram
#
# CHANGELOG (Max 5 entries):
#   - v1.1.0 (2026-02-18): DPLAN-005 - Add silent mode, CLI interface for cross-branch use, markdown support
#   - v1.0.0 (2026-02-17): Initial implementation - reusable Telegram notification sender
#
# CODE STANDARDS:
#   - Handlers implement logic, modules orchestrate
#   - No cross-branch imports, no Prax logger
# =============================================

"""
Telegram notification sender for the scheduler bot.

Can be used two ways:
1. Import (within API branch): send_telegram_notification("message")
2. CLI (cross-branch, no import guard): python3 notifier.py "message"
   Flags: --silent (silent push), --markdown (Markdown parse mode)

Reads bot token and chat_id from ~/.aipass/scheduler_config.json.
"""

# Infrastructure
import sys
from pathlib import Path

# Standard library
import json
from urllib.request import Request, urlopen
from urllib.error import URLError

# =============================================
# CONSTANTS
# =============================================

CONFIG_PATH = Path.home() / ".aipass" / "scheduler_config.json"

# =============================================
# PUBLIC API
# =============================================


def send_telegram_notification(
    message: str,
    silent: bool = False,
    parse_mode: str | None = None,
) -> bool:
    """
    Send a message to Telegram via the scheduler bot.

    Args:
        message: Text to send (plain text or Markdown)
        silent: If True, send as silent notification (no sound on phone)
        parse_mode: Telegram parse mode ("Markdown" or "HTML"). None for plain text.

    Returns:
        True if sent successfully, False otherwise
    """
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        bot_token = config["telegram_bot_token"]
        chat_id = config["telegram_chat_id"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload_dict: dict[str, object] = {"chat_id": chat_id, "text": message}
    if silent:
        payload_dict["disable_notification"] = True
    if parse_mode:
        payload_dict["parse_mode"] = parse_mode

    data = json.dumps(payload_dict).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False)
    except (URLError, Exception):
        return False


# =============================================
# CLI INTERFACE (cross-branch use)
# =============================================

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: python3 notifier.py [--silent] [--markdown] \"message\"")
        print("  --silent    Send as silent notification (no sound)")
        print("  --markdown  Use Telegram Markdown parse mode")
        sys.exit(0)

    silent_flag = "--silent" in args
    markdown_flag = "--markdown" in args
    msg_args = [a for a in args if not a.startswith("--")]

    if not msg_args:
        print("Error: no message provided", file=sys.stderr)
        sys.exit(1)

    msg = " ".join(msg_args)
    mode = "Markdown" if markdown_flag else None
    ok = send_telegram_notification(msg, silent=silent_flag, parse_mode=mode)
    sys.exit(0 if ok else 1)
