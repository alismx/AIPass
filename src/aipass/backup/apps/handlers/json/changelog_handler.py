
# ===================AIPASS====================
# META DATA HEADER
# Name: changelog_handler.py - Backup changelog management
# Date: 2025-11-16
# Version: 1.0.0
# Category: handlers
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2025-11-16): Initial extraction from backup_core.py
#     * load_changelog() - Load persistent changelog
#     * save_changelog_entry() - Add new entry
#     * display_previous_comments() - Show history
#
# CODE STANDARDS:
#   - Follow seed 3-layer architecture
#   - Handlers must be independent and transportable
#   - No cross-handler imports except within same domain
# =============================================

"""
Backup Changelog Handler

Manages persistent changelog of backup operations with notes/comments.
Tracks all backup operations with timestamps and user notes for history tracking.

Functions:
    load_changelog: Load changelog from JSON file
    save_changelog_entry: Add timestamped entry to changelog
    display_previous_comments: Display recent entries to user
"""

# =============================================
# IMPORTS
# =============================================

import json
import logging
import datetime
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)

from rich.console import Console

# Initialize console for output
console = Console()

# =============================================
# CHANGELOG OPERATIONS
# =============================================

def load_changelog(changelog_file: Path) -> Dict:
    """Load persistent changelog of backup comments.

    Args:
        changelog_file: Path to changelog JSON file

    Returns:
        Dictionary with 'entries' list (empty dict if file missing)
    """
    if changelog_file.exists():
        try:
            with open(changelog_file, 'r', encoding='utf-8', errors='replace') as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[red]Error loading changelog: {e}[/red]")
            logger.warning(f"Error loading changelog: {e}")
    return {"entries": []}


def save_changelog_entry(changelog_file: Path, note: str, mode: str,
                        backup_path: Path) -> bool:
    """Add new entry to persistent changelog.

    Args:
        changelog_file: Path to changelog JSON file
        note: User note describing the backup
        mode: Backup mode ('snapshot' or 'versioned')
        backup_path: Path to backup destination

    Returns:
        True if save succeeded, False otherwise
    """
    try:
        changelog = load_changelog(changelog_file)
        new_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "note": note,
            "mode": mode,
            "backup_path": str(backup_path)
        }
        changelog["entries"].append(new_entry)

        with open(changelog_file, 'w', encoding='utf-8') as f:
            json.dump(changelog, f, indent=2, ensure_ascii=False)
        logger.info(f"[changelog_handler] Saved changelog entry: {note[:50]}")
        return True
    except Exception as e:
        console.print(f"[red]Error saving changelog entry: {e}[/red]")
        logger.error(f"[changelog_handler] Error saving changelog: {e}")
        return False


def display_previous_comments(changelog_file: Path, mode_name: str):
    """Display previous backup comments with mode identification.

    Args:
        changelog_file: Path to changelog JSON file
        mode_name: Display name of backup mode ('System Snapshot', etc.)
    """
    try:
        changelog = load_changelog(changelog_file)
        entries = changelog.get("entries", [])

        if not entries:
            console.print(f"[yellow]No previous {mode_name} backup comments found.[/yellow]")
            return

        from rich.panel import Panel
        console.print()
        console.print(Panel(f"PREVIOUS {mode_name.upper()} BACKUP COMMENTS",
                           style="bold cyan",
                           border_style="cyan"))

        # Show last 10 entries (most recent first)
        recent_entries = entries[-10:]
        for i, entry in enumerate(reversed(recent_entries), 1):
            try:
                timestamp = datetime.datetime.fromisoformat(entry["timestamp"])
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M")
                mode_info = entry.get('mode', 'unknown')
                # Handle encoding issues in notes
                note = str(entry['note']).encode('ascii', errors='replace').decode('ascii')
                console.print(f"[bright_blue]{i:2d}.[/bright_blue] [{formatted_time}] [green][{mode_info}][/green] {note}")
            except Exception as e:
                console.print(f"[bright_blue]{i:2d}.[/bright_blue] [red][ERROR] Failed to display entry: {e}[/red]")

        if len(entries) > 10:
            console.print(f"\n[dim]... and {len(entries) - 10} older entries[/dim]")
        console.print()
    except FileNotFoundError:
        console.print(f"[yellow]No previous {mode_name} backup comments found.[/yellow]")
    except PermissionError as e:
        console.print(f"[yellow]Warning: Cannot read backup history - permission denied: {e}[/yellow]")
        console.print("[yellow]Continuing with backup...[/yellow]")
    except Exception as e:
        console.print(f"[yellow]Warning: Error displaying comments: {e}[/yellow]")
        console.print("[yellow]Continuing with backup...[/yellow]")


# =============================================
# MODULE INITIALIZATION
# =============================================

# No module-level initialization needed
