
# ===================AIPASS====================
# META DATA HEADER
# Name: log_streamer.py - Stream system logs to Telegram
# Date: 2026-02-26
# Version: 1.0.0
# Category: api/handlers/telegram
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-02-26): Initial - daemon thread log tailing with batched Telegram delivery
#
# CODE STANDARDS:
#   - Uses Prax get_direct_logger() — no event pipeline (FPLAN-0382 migration)
#   - Silent failure on Telegram errors (log warning, never crash)
#   - Handlers implement logic, modules orchestrate
# =============================================

"""
LogStreamer - Stream system log lines to a Telegram chat.

v1.0.0

Runs as a background daemon thread, tailing log files for a specific branch
and batching new lines to send via the Telegram Bot API. Tracks file positions
to only deliver new content, handles file rotation, and discovers new log files
each cycle.

Usage:
    streamer = LogStreamer(bot_token="...", chat_id=123456, branch_name="api")
    streamer.start()
    # ... later ...
    streamer.stop()
"""

# Infrastructure
import sys
from pathlib import Path

# Standard library
import json
import threading
from typing import Dict, List
from urllib.error import URLError
from urllib.request import Request, urlopen

# Logging (Prax direct logger — FPLAN-0382, no event pipeline)
from aipass.prax.apps.modules.logger import get_direct_logger

# =============================================
# CONSTANTS
# =============================================

def _find_repo_root() -> Path:
    """Walk up from this file to find AIPASS_REGISTRY.json (repo root)."""
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "AIPASS_REGISTRY.json").exists():
            return parent
    return Path.cwd()

SYSTEM_LOGS_DIR = _find_repo_root() / "logs"
BATCH_INTERVAL = 5.0
TELEGRAM_MAX_LENGTH = 4000


# =============================================
# LOG STREAMER
# =============================================


class LogStreamer:
    """Stream system log lines for a branch to Telegram via batched sends."""

    def __init__(self, bot_token: str, chat_id: int, branch_name: str) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.branch_name = branch_name

        self._running = False
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self.log_positions: Dict[str, int] = {}

        # Direct logger (no event pipeline — avoids recursion with log tailing)
        self.logger = get_direct_logger()

        # Initialize positions to end of all existing log files
        self._init_positions()

    # -----------------------------------------
    # POSITION TRACKING
    # -----------------------------------------

    def _get_log_files(self) -> List[Path]:
        """Find all log files matching this branch's pattern."""
        if not SYSTEM_LOGS_DIR.exists():
            return []
        return sorted(SYSTEM_LOGS_DIR.glob(f"{self.branch_name}_*.log"))

    def _init_positions(self) -> None:
        """Set initial positions to end of file so we only tail new lines."""
        for log_file in self._get_log_files():
            file_path = str(log_file)
            try:
                self.log_positions[file_path] = log_file.stat().st_size
            except OSError:
                self.log_positions[file_path] = 0
        self.logger.info(
            "Initialized positions for %d log files (branch: %s)",
            len(self.log_positions), self.branch_name
        )

    def _read_new_lines(self) -> List[str]:
        """Read new lines from all tracked log files."""
        all_new_lines: List[str] = []

        for log_file in self._get_log_files():
            file_path = str(log_file)

            try:
                current_size = log_file.stat().st_size
            except OSError:
                continue

            last_pos = self.log_positions.get(file_path, 0)

            try:
                # New file discovered mid-run: start from beginning
                if file_path not in self.log_positions:
                    last_pos = 0
                    self.logger.info("New log file discovered: %s", file_path)

                # File rotation: size shrank, reset to beginning
                if current_size < last_pos:
                    self.logger.info("File rotation detected: %s", file_path)
                    last_pos = 0

                # Read new content
                if current_size > last_pos:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        f.seek(last_pos)
                        new_content = f.read()
                        self.log_positions[file_path] = f.tell()

                    lines = new_content.splitlines()
                    if lines:
                        all_new_lines.extend(lines)
                else:
                    # Update position even when nothing new (handles new file registration)
                    self.log_positions[file_path] = current_size
            except OSError as e:
                self.logger.warning("Failed to process %s: %s", file_path, e)
                continue

        return all_new_lines

    # -----------------------------------------
    # TELEGRAM DELIVERY
    # -----------------------------------------

    def _send_message(self, message: str) -> bool:
        """Send a message to Telegram. Returns True on success."""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = json.dumps({
            "chat_id": self.chat_id,
            "text": message,
            "disable_notification": True
        }).encode("utf-8")
        req = Request(url, data=payload, headers={"Content-Type": "application/json"})

        try:
            with urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())
                return result.get("ok", False)
        except (URLError, Exception) as e:
            self.logger.warning("Telegram send failed: %s", e)
            return False

    def _send_batched(self, lines: List[str]) -> None:
        """Split lines into messages respecting TELEGRAM_MAX_LENGTH, send each."""
        if not lines:
            return

        batch: List[str] = []
        batch_len = 0

        for line in lines:
            # +1 for the newline separator between lines
            line_len = len(line) + (1 if batch else 0)

            if batch_len + line_len > TELEGRAM_MAX_LENGTH and batch:
                # Send current batch
                message = "\n".join(batch)
                self._send_message(message)
                batch = []
                batch_len = 0

            batch.append(line)
            batch_len += line_len

        # Send remaining
        if batch:
            message = "\n".join(batch)
            self._send_message(message)

    # -----------------------------------------
    # DAEMON THREAD
    # -----------------------------------------

    def _run(self) -> None:
        """Main loop: read new lines, batch, send, sleep."""
        self.logger.info("Log streamer started for branch: %s", self.branch_name)
        self.logger.info("Watching: %s/%s_*.log (chat_id=%s)", SYSTEM_LOGS_DIR, self.branch_name, self.chat_id)

        while self._running:
            try:
                new_lines = self._read_new_lines()
                if new_lines:
                    self.logger.info("Found %d new log lines, sending to Telegram", len(new_lines))
                    self._send_batched(new_lines)
            except Exception as e:
                self.logger.warning("Streamer cycle error: %s", e)

            # Interruptible sleep
            self._stop_event.wait(BATCH_INTERVAL)

        self.logger.info("Log streamer stopped for branch: %s", self.branch_name)

    # -----------------------------------------
    # PUBLIC API
    # -----------------------------------------

    def start(self) -> None:
        """Start the log streamer daemon thread."""
        if self._running:
            self.logger.warning("Log streamer already running")
            return

        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name=f"log-streamer-{self.branch_name}",
            daemon=True
        )
        self._thread.start()
        self.logger.info("Daemon thread started: %s", self._thread.name)

    def stop(self) -> None:
        """Stop the log streamer and wait for thread to finish."""
        if not self._running:
            return

        self._running = False
        self._stop_event.set()

        if self._thread is not None:
            self._thread.join(timeout=BATCH_INTERVAL + 2)
            if self._thread.is_alive():
                self.logger.warning("Daemon thread did not exit cleanly")
            self._thread = None

        self.logger.info("Log streamer stopped")
