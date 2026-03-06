#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: config.py - Telegram Configuration Handler
# Date: 2026-02-03
# Version: 1.2.0
# Category: api/handlers/telegram
#
# CHANGELOG (Max 5 entries):
#   - v1.2.0 (2026-02-24): Add multi-bot config: load_bot_config, list_bot_configs, validate_bot_config
#   - v1.1.0 (2026-02-03): Add allowed_user_ids loading for user allowlist
#   - v1.0.0 (2026-02-03): Initial config loader for Telegram bridge
#
# CODE STANDARDS:
#   - Pure functions with proper error raising
#   - No Prax imports (handler tier 3)
# =============================================

"""
Telegram Configuration Handler

Manages Telegram bot configuration:
- Load bot token from config file (legacy single-bot: ~/.aipass/telegram_config.json)
- Load bot username
- Load allowed user IDs for access control
- Load per-bot configs (multi-bot: ~/.aipass/telegram_bots/{bot_id}.json)
- List and validate bot configs
"""

# Infrastructure
import sys
from pathlib import Path

# Standard library
import json
from typing import Optional, List

# =============================================
# CONSTANTS
# =============================================

CONFIG_PATH = Path.home() / ".aipass" / "telegram_config.json"
BOT_CONFIG_DIR = Path.home() / ".aipass" / "telegram_bots"

REQUIRED_BOT_FIELDS = ("bot_id", "bot_token")

# =============================================
# CONFIGURATION LOADING
# =============================================

def load_telegram_config() -> Optional[dict]:
    """
    Load Telegram configuration from config file.

    Config file location: ~/.aipass/telegram_config.json
    Expected structure:
    {
        "telegram_bot_token": "...",
        "telegram_bot_username": "aipass_bridge_bot",
        "allowed_user_ids": []
    }

    Returns:
        Configuration dict or None if load fails
    """
    try:
        if not CONFIG_PATH.exists():
            return None

        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)

        return config

    except json.JSONDecodeError:
        return None
    except Exception:
        return None


def get_bot_token() -> Optional[str]:
    """
    Get Telegram bot token from config.

    Returns:
        Bot token string or None if not found
    """
    config = load_telegram_config()
    if not config:
        return None

    token = config.get("telegram_bot_token")
    if not token:
        return None

    return token


def get_bot_username() -> Optional[str]:
    """
    Get Telegram bot username from config.

    Returns:
        Bot username string or None if not found
    """
    config = load_telegram_config()
    if not config:
        return None

    username = config.get("telegram_bot_username")
    if not username:
        return None

    return username


def get_allowed_user_ids() -> List[int]:
    """
    Get list of allowed Telegram user IDs from config.

    Returns:
        List of allowed user IDs. Empty list means allow all (for testing).
    """
    config = load_telegram_config()
    if not config:
        return []

    allowed = config.get("allowed_user_ids", [])
    if not isinstance(allowed, list):
        return []

    return [int(uid) for uid in allowed if isinstance(uid, (int, str))]


def validate_config() -> bool:
    """
    Validate that Telegram configuration is complete.

    Returns:
        True if config is valid, False otherwise
    """
    config = load_telegram_config()
    if not config:
        return False

    if not config.get("telegram_bot_token"):
        return False

    return True


# =============================================
# MULTI-BOT CONFIGURATION (per-bot configs)
# =============================================


def load_bot_config(bot_id: str) -> dict | None:
    """
    Load per-bot config from ~/.aipass/telegram_bots/{bot_id}.json.

    Config format:
    {
        "bot_id": "dev_central",
        "bot_token": "123:ABC...",
        "bot_name": "AIPass Dev Central Bot",
        "branch_name": "dev_central",  // null for base bot
        "work_dir": "/home/aipass/aipass_os/dev_central",
        "allowed_user_ids": [7235222625]
    }

    Args:
        bot_id: Bot identifier matching the config filename.

    Returns:
        Config dict or None if not found/invalid.
    """
    config_path = BOT_CONFIG_DIR / f"{bot_id}.json"

    try:
        if not config_path.exists():
            return None

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        if not isinstance(config, dict):
            return None

        return config

    except json.JSONDecodeError:
        return None
    except OSError:
        return None


def list_bot_configs() -> list[str]:
    """
    List all bot config files (returns list of bot_ids).

    Scans ~/.aipass/telegram_bots/ for .json files, excluding
    internal files that start with underscore (e.g., _registry.json).

    Returns:
        List of bot_id strings derived from config filenames.
    """
    if not BOT_CONFIG_DIR.exists():
        return []

    bot_ids = []
    try:
        for path in sorted(BOT_CONFIG_DIR.glob("*.json")):
            # Skip internal files (e.g., _registry.json)
            if path.stem.startswith("_"):
                continue
            bot_ids.append(path.stem)
    except OSError:
        return []

    return bot_ids


def validate_bot_config(config: object) -> tuple[bool, str]:
    """
    Validate a bot config dict.

    Checks for required fields and basic type correctness.

    Args:
        config: Bot config dict to validate.

    Returns:
        Tuple of (valid, error_message). error_message is empty on success.
    """
    if not isinstance(config, dict):
        return False, "Config must be a dict"

    # Check required fields
    for field in REQUIRED_BOT_FIELDS:
        if not config.get(field):
            return False, f"Missing required field: {field}"

    # Type checks
    bot_token = config.get("bot_token", "")
    if not isinstance(bot_token, str) or ":" not in bot_token:
        return False, "bot_token must be a string in format 'id:hash'"

    if "work_dir" in config and config["work_dir"] is not None:
        work_dir = Path(config["work_dir"])
        if not work_dir.is_absolute():
            return False, "work_dir must be an absolute path"

    if "allowed_user_ids" in config:
        allowed = config["allowed_user_ids"]
        if not isinstance(allowed, list):
            return False, "allowed_user_ids must be a list"

    return True, ""
