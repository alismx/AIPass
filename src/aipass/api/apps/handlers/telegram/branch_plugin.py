
# ===================AIPASS====================
# META DATA HEADER
# Name: branch_plugin.py - BranchPlugin extends BaseBot for per-branch bots
# Date: 2026-02-24
# Version: 1.0.0
# Category: api/handlers/telegram
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-02-24): Initial - BranchPlugin with message prefixing and startup injection
#
# CODE STANDARDS:
#   - Inherits Prax get_direct_logger() from BaseBot (FPLAN-0382 migration)
#   - Extends BaseBot via hook overrides
#   - No duplicated logic - all core behavior lives in BaseBot
# =============================================

"""
BranchPlugin - Per-branch Telegram bot extending BaseBot.

Each AIPass branch gets its own dedicated Telegram bot. BranchPlugin overrides
BaseBot's hooks to:
  - Prefix incoming messages with "Patrick via Telegram: "
  - Prefix outgoing responses with "@branch_name"
  - Inject "hi" on session creation to trigger the branch startup protocol

Usage:
    bot = BranchPlugin(
        branch_name="dev_central",
        bot_id="dev_central",
        bot_token="123:ABC",
        work_dir=Path.cwd(),
        bot_name="AIPass Dev Central Bot",
        allowed_user_ids=[7235222625],
    )
    sys.exit(bot.run())
"""

# Infrastructure
import os
import sys
from pathlib import Path

# Standard library
import argparse
import json
import time

# Sibling import
from aipass.api.apps.handlers.telegram.base_bot import BaseBot


# =============================================
# BranchPlugin CLASS
# =============================================

class BranchPlugin(BaseBot):
    """
    Per-branch Telegram bot that extends BaseBot with branch-specific behavior.

    Overrides BaseBot hooks to prefix messages, tag responses, and trigger
    the AIPass startup protocol when a new tmux session is created.
    """

    def __init__(self, branch_name: str, **kwargs) -> None:
        """
        Initialize BranchPlugin.

        Args:
            branch_name: AIPass branch name (e.g., "dev_central", "seed")
            **kwargs: All BaseBot constructor arguments (bot_id, bot_token, etc.)
        """
        self.branch_name = branch_name
        super().__init__(**kwargs)

    # =============================================
    # HOOK OVERRIDES
    # =============================================

    def on_message(self, text: str) -> str:
        """
        Prefix incoming messages with sender attribution.

        Args:
            text: Raw message text from Telegram

        Returns:
            Prefixed text for Claude: "Patrick via Telegram: {text}"
        """
        return f"Patrick via Telegram: {text}"

    def on_response(self, text: str) -> str:
        """
        Prefix outgoing responses with branch tag.

        Args:
            text: Raw response text from Claude

        Returns:
            Tagged text: "@{branch_name}\n{text}"
        """
        return f"@{self.branch_name}\n{text}"

    def on_session_create(self, session_name: str, work_dir: Path) -> None:
        """
        Inject "hi" after tmux session creation to trigger startup protocol.

        Waits 2 seconds for Claude to fully initialize, then injects "hi"
        which triggers the AIPass startup sequence (reading memories, etc.).

        Args:
            session_name: The tmux session name that was created
            work_dir: The working directory of the session
        """
        self.logger.info(
            "Branch session created for @%s, injecting startup greeting",
            self.branch_name,
        )
        time.sleep(2)
        self.inject_message("hi")


# =============================================
# CLI ENTRY POINT
# =============================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AIPass Telegram Branch Bot")
    parser.add_argument("--bot-id", required=True, help="Bot identifier")
    parser.add_argument("--config", help="Path to bot config JSON")
    args = parser.parse_args()

    # Load config from data dir telegram_bots/{bot_id}.json or --config path
    _env_data = os.environ.get("AIPASS_DATA_DIR")
    _data_dir = Path(_env_data) if _env_data else (
        Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "aipass"
    )
    config_path = (
        Path(args.config)
        if args.config
        else _data_dir / "telegram_bots" / f"{args.bot_id}.json"
    )

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # If config has "branch_name", create BranchPlugin; otherwise BaseBot
    shared_session = config.get("shared_session")

    if config.get("branch_name"):
        bot = BranchPlugin(
            branch_name=config["branch_name"],
            bot_id=args.bot_id,
            bot_token=config["bot_token"],
            work_dir=Path(config["work_dir"]),
            bot_name=config.get("bot_name", f"AIPass {config['branch_name']} Bot"),
            allowed_user_ids=config.get("allowed_user_ids", []),
            shared_session=shared_session,
        )
    else:
        bot = BaseBot(
            bot_id=args.bot_id,
            bot_token=config["bot_token"],
            work_dir=Path(config.get("work_dir", str(Path.cwd()))),
            bot_name=config.get("bot_name", "AIPass Bot"),
            allowed_user_ids=config.get("allowed_user_ids", []),
            shared_session=shared_session,
        )

    sys.exit(bot.run())
