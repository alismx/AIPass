# =================== AIPass ====================
# Name: compass_wrapper.py
# Description: Scaffold for devpulse private Compass personal layer
# Version: 0.1.0
# Created: 2026-04-14
# Modified: 2026-04-14
# =============================================

"""Devpulse -> Compass personal layer wrapper (SCAFFOLD / STUB).

This module is the intended entry point for devpulse's private Compass
personal layer. It is a scaffold only -- no logic is implemented yet.

Design doc:
    src/aipass/devpulse/.trinity/night_shift_reports/compass_layer_design.md

Storage (gitignored, never committed):
    src/aipass/devpulse/.trinity/compass/
        devpulse_config.json   -- collection identity / metadata
        ingest_log.jsonl       -- idempotency log for ingest attempts
        .chroma/               -- future ChromaDB data directory

Intended interface:
    - query_top(context, n)            -> top-N relevant fragments
    - ingest_learning(key, text, sid)  -> write a new learning fragment
    - stats()                          -> collection health / counts

No ``chromadb`` import is performed here on purpose: we don't want to
pull the dependency in until the real implementation lands. A future
session will replace the ``NotImplementedError`` bodies with actual
Compass engine calls (via subprocess or a direct import from the
Compass navigator package).
"""

from __future__ import annotations

from pathlib import Path

from aipass.prax import logger
from aipass.cli.apps.modules import console, err_console

MODULE_NAME = "compass_wrapper"


# =============================================================================
# PUBLIC INTERFACE (stub)
# =============================================================================

def query_top(context: str, n: int = 5) -> list[dict]:
    """Query the devpulse-compass layer for top-N fragments matching the context."""
    raise NotImplementedError("compass_wrapper.query_top not yet implemented")


def ingest_learning(learning_key: str, learning_text: str, session_id: int) -> bool:
    """Ingest a new learning into the devpulse-compass layer."""
    raise NotImplementedError("compass_wrapper.ingest_learning not yet implemented")


def stats() -> dict:
    """Return collection stats: fragment count, last ingest, schema version."""
    raise NotImplementedError("compass_wrapper.stats not yet implemented")


# =============================================================================
# INTROSPECTION
# =============================================================================

def print_introspection() -> None:
    """Print module introspection -- scaffold status and intended interface."""
    console.print("[bold cyan]compass_wrapper[/bold cyan] -- devpulse private Compass layer (SCAFFOLD)")
    console.print("  status: stub / not implemented")
    console.print("  storage: .trinity/compass/ (gitignored)")
    console.print("  interface:")
    console.print("    - query_top(context, n)")
    console.print("    - ingest_learning(learning_key, learning_text, session_id)")
    console.print("    - stats()")
    console.print("  design: .trinity/night_shift_reports/compass_layer_design.md")


# =============================================================================
# HANDLER SECURITY GUARD
# =============================================================================

def handle_command(command: str, args: list) -> bool:
    """Entry point for drone routing. Guards against cross-branch imports misuse."""
    caller = Path.cwd().name
    if caller != "devpulse" and not any(
        p.name == "devpulse" for p in Path.cwd().parents
    ):
        logger.warning(
            f"[COMPASS_WRAPPER] Cross-branch call from {caller} -- use ai_mail instead"
        )
        return False

    if command != "compass":
        return False

    if not args or args[0] in ("--help", "-h", "help"):
        print_introspection()
        return True

    # All subcommands are stubs until implementation lands.
    err_console.print(
        "[yellow]compass_wrapper is a scaffold -- no subcommands implemented yet.[/yellow]"
    )
    err_console.print("See design doc: .trinity/night_shift_reports/compass_layer_design.md")
    return True
