#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: errors.py - Error Registry Management Module
# Date: 2026-02-13
# Version: 1.2.0
# Category: trigger/modules
#
# CHANGELOG (Max 5 entries):
#   - v1.2.0 (2026-02-14): Public API report_error() for cross-branch push reporting
#   - v1.1.0 (2026-02-13): Phase 5 - Source fix pipeline (email + fix status tracking)
#   - v1.0.0 (2026-02-13): Created - Phase 4 Medic v2 management commands
#
# CODE STANDARDS:
#   - Follows AIPass Seed standards
#   - Module orchestrates, handler (error_registry.py) contains data logic
#   - No direct file operations - delegates to handler
# =============================================

"""
Error Registry Management - View and control tracked errors

Commands for viewing, filtering, and managing errors in the Medic v2
error registry. Provides visibility into all tracked errors with
fingerprinting, counts, and status tracking.

Commands: list, detail, suppress, resolve, clear-resolved, stats, circuit-breaker
Public API: report_error() for cross-branch push reporting (Drone calls this)
Phase 5: Suppress triggers source fix pipeline (email + fix status tracking)
Architecture: Module orchestrates, error_registry handler manages data
"""

import sys
import time
from pathlib import Path
from typing import Optional


from aipass.prax.apps.modules.logger import system_logger as logger
from aipass.trigger.apps.handlers.error_registry import (
    query, get_entry, update_status, clear_resolved, get_stats,
    get_circuit_breaker_status, circuit_breaker_reset,
    update_source_fix_status,
    report as _registry_report,
)

def report_error(
    error_type: str,
    message: str,
    component: str,
    log_path: str = "",
    severity: str = "medium",
    fire_event: bool = True
) -> dict:
    """Report an error to the registry and optionally fire error_detected event.

    Public API for cross-branch push reporting. Drone and other branches
    call this instead of importing from handlers directly.

    Pipeline: report() -> registry stores -> fire event -> handler checks
    circuit breaker + rate limiting -> dispatch email if allowed.

    Args:
        error_type: Error class name (e.g., 'ImportError', 'TimeoutError')
        message: Original error message text
        component: Branch that generated the error (e.g., 'FLOW', 'API')
        log_path: Path to source log file (optional)
        severity: Error severity - low, medium, high, critical (default: medium)
        fire_event: Whether to fire error_detected event (default: True).
            Set False for silent registration without dispatch.

    Returns:
        Dict with error entry data + 'is_new' bool + 'dispatched' bool.
    """
    result = _registry_report(
        error_type=error_type,
        message=message,
        component=component,
        log_path=log_path,
        severity=severity,
    )
    result["dispatched"] = False

    # Fire event on first occurrence (count==1) for registration and on
    # second occurrence (count==2) so the handler can apply the dispatch
    # threshold.  Skip all other counts (backoff handles later dispatches).
    error_count = result.get("count", 1)
    if not fire_event or (not result.get("is_new", False) and error_count != 2):
        return result

    try:
        from aipass.trigger.apps.modules.core import trigger as _trigger_bus
        _trigger_bus.fire(
            "error_detected",
            branch=component,
            module=error_type,
            message=message,
            log_path=log_path,
            error_hash=result.get("id", ""),
            timestamp=result.get("last_seen", ""),
            fingerprint=result.get("fingerprint", ""),
            registry_id=result.get("id", ""),
            first_seen=result.get("first_seen", ""),
            last_seen=result.get("last_seen", ""),
            count=error_count,
        )
        result["dispatched"] = True
    except Exception:
        pass

    return result


_STATUS_COLORS = {"new": "yellow", "investigating": "cyan", "suppressed": "dim", "resolved": "green"}
_SEVERITY_COLORS = {"low": "dim", "medium": "yellow", "high": "red", "critical": "bold red"}
_CB_COLORS = {"closed": "green", "open": "red", "half_open": "yellow"}
_FIX_STATUS_COLORS = {"none": "dim", "pending_fix": "yellow", "fix_requested": "cyan", "fix_confirmed": "green"}


def _parse_args(args: list) -> dict:
    """Parse --key=value arguments into a dict (keys without leading --)."""
    parsed = {}
    for arg in args:
        if arg.startswith("--") and "=" in arg:
            key, value = arg.split("=", 1)
            parsed[key.lstrip("-")] = value
    return parsed


def _find_by_id_or_fp(identifier: str) -> Optional[dict]:
    """Look up error by fingerprint (prefix ok) or short ID field."""
    entry = get_entry(identifier)
    if entry:
        return entry
    for entry in query(limit=1000):
        if entry.get("id") == identifier:
            return entry
    return None


def _fmt_time(iso: str) -> str:
    """Trim ISO timestamp to 'YYYY-MM-DD HH:MM:SS'."""
    if "T" in iso and "." in iso:
        return iso.split(".")[0].replace("T", " ")
    if "T" in iso:
        return iso.replace("T", " ")
    return iso


def print_help() -> None:
    """Print module help using Rich formatting."""
    from aipass.cli.apps.modules import console
    from rich.panel import Panel

    console.print(Panel("Error Registry - Medic v2 Error Management", style="bold"))
    console.print()
    console.print("View and manage tracked errors in the Medic v2 error registry.")
    console.print()
    console.rule("USAGE")
    console.print()
    console.print("  drone @trigger errors <command>")
    console.print("  python3 trigger.py errors <command>")
    console.print()
    console.rule("COMMANDS")
    console.print()
    console.print("  [bold]list[/bold]               List tracked errors (default)")
    console.print("                       [dim]--status=new --component=FLOW --severity=high --limit=20[/dim]")
    console.print("  [bold]detail[/bold] <id>         Show full details for an error entry")
    console.print("  [bold]suppress[/bold] <id> [reason]  Mark error as suppressed")
    console.print("  [bold]resolve[/bold] <id>        Mark error as resolved")
    console.print("  [bold]clear-resolved[/bold]      Purge old resolved entries [dim](--days=7)[/dim]")
    console.print("  [bold]stats[/bold]               Summary statistics + circuit breaker state")
    console.print("  [bold]circuit-breaker[/bold]      Show or reset circuit breaker [dim](reset)[/dim]")
    console.print("  [bold]help[/bold]               Show this help")
    console.print()
    console.rule("EXAMPLES")
    console.print()
    console.print("  drone @trigger errors list --status=new --component=FLOW")
    console.print("  drone @trigger errors detail a1b2c3d4")
    console.print("  drone @trigger errors suppress a1b2c3d4 known startup issue")
    console.print("  drone @trigger errors resolve a1b2c3d4")
    console.print("  drone @trigger errors clear-resolved --days=14")
    console.print("  drone @trigger errors circuit-breaker reset")
    console.print()


def handle_command(command: str, args: list) -> bool:
    """Handle error management commands.

    Args:
        command: Module name (errors)
        args: Additional arguments

    Returns:
        True if command was handled, False otherwise
    """
    from aipass.cli.apps.modules import console

    if command != "errors":
        return False

    if not args:
        return _cmd_list(console, [])
    if args[0] in ['--help', '-h', 'help']:
        print_help()
        return True

    sub = args[0]
    rest = args[1:]

    routes = {
        "list": _cmd_list, "detail": _cmd_detail, "suppress": _cmd_suppress,
        "resolve": _cmd_resolve, "clear-resolved": _cmd_clear_resolved,
        "stats": _cmd_stats, "circuit-breaker": _cmd_circuit_breaker,
    }

    if sub in routes:
        return routes[sub](console, rest)

    console.print(f"[red]Unknown subcommand: {sub}[/red]")
    console.print("Run [dim]drone @trigger errors help[/dim] for available commands")
    return True


# ---------------------------------------------------------------------------
# Source Fix Pipeline
# ---------------------------------------------------------------------------

def _send_source_fix_email(entry: dict) -> bool:
    """Send recommendation email to source branch about fixing log level.

    When an error is suppressed, the source branch gets notified that
    their log level may be wrong. This closes the loop:
    error -> investigate -> suppress -> fix source -> error stops

    Args:
        entry: Error registry entry dict

    Returns:
        True if email sent successfully
    """
    try:
        from aipass.ai_mail.apps.modules.email import send_email_direct
    except ImportError:
        logger.info("[ERRORS] Could not import send_email_direct - ai_mail not available")
        return False

    try:
        component = entry.get("component", "").lower()
        if not component or component == "unknown":
            return False

        recipient = f"@{component}"
        fingerprint = entry.get("fingerprint", "")[:12]
        error_type = entry.get("error_type", "?")
        message = entry.get("message", "?")[:200]
        suppress_reason = entry.get("suppress_reason", "No reason")
        log_path = entry.get("log_path", "unknown")
        count = entry.get("count", 0)

        subject = f"[LOG FIX] {error_type} classified as non-critical"

        body = f"""Your code is generating an error that has been classified as non-critical.

Error fingerprint: {fingerprint}
Error type: {error_type}
Occurrences: {count}
Log file: {log_path}
Suppress reason: {suppress_reason}

Error message:
{message}

RECOMMENDATION:
This error is currently logged as ERROR but appears to be non-critical based on
investigation. Consider one of:
1. Change the log level from ERROR to WARNING or INFO
2. Add proper error handling to prevent this from being logged
3. If this is actually critical, reply to @trigger explaining why

This will prevent unnecessary error dispatch for this issue.

---
Automated recommendation from Medic v2 Error Registry.
Reply to @trigger with your fix status."""

        send_email_direct(
            to_branch=recipient,
            subject=subject,
            message=body,
            reply_to='@trigger',
            from_branch='@trigger'
        )

        logger.info(f"[ERRORS] Source fix email sent to {recipient} for {fingerprint}")
        return True
    except Exception as exc:
        logger.info(f"[ERRORS] Failed to send source fix email: {exc}")
        return False


# ---------------------------------------------------------------------------
# Command implementations
# ---------------------------------------------------------------------------

def _cmd_list(console, args: list) -> bool:
    """List errors with Rich table. Filters: --status, --component, --severity, --limit."""
    from rich.table import Table

    parsed = _parse_args(args)
    sf, cf, svf = parsed.get("status"), parsed.get("component"), parsed.get("severity")
    limit = int(parsed.get("limit", "50"))

    entries = query(status=sf, component=cf, severity=svf, limit=limit)

    if not entries:
        console.print("[dim]No errors in registry[/dim]")
        if sf or cf or svf:
            console.print(f"  [dim]Filters: status={sf} component={cf} severity={svf}[/dim]")
        return True

    filters = [f"{k}={v}" for k, v in [("status", sf), ("component", cf), ("severity", svf)] if v]
    ftxt = f" ({', '.join(filters)})" if filters else ""

    table = Table(title=f"Error Registry{ftxt}")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Fingerprint", style="dim", width=10)
    table.add_column("Type", width=18)
    table.add_column("Component", width=12)
    table.add_column("Count", justify="right", width=6)
    table.add_column("Severity", width=10)
    table.add_column("Status", width=14)
    table.add_column("Last Seen", width=19)

    for e in entries:
        sev = e.get("severity", "?")
        st = e.get("status", "?")
        sc = _STATUS_COLORS.get(st, "white")
        svc = _SEVERITY_COLORS.get(sev, "white")
        table.add_row(
            e.get("id", "?"), e.get("fingerprint", "?")[:8],
            e.get("error_type", "?"), e.get("component", "?"),
            str(e.get("count", 0)),
            f"[{svc}]{sev}[/{svc}]", f"[{sc}]{st}[/{sc}]",
            _fmt_time(e.get("last_seen", "?")),
        )

    console.print(table)
    console.print(f"  [dim]Showing {len(entries)} error(s) (limit {limit})[/dim]")
    return True


def _cmd_detail(console, args: list) -> bool:
    """Show full error details for a fingerprint or ID."""
    from rich.panel import Panel

    if not args:
        console.print("[red]Missing error ID or fingerprint[/red]")
        console.print("Usage: drone @trigger errors detail <id_or_fingerprint>")
        return True

    entry = _find_by_id_or_fp(args[0])
    if not entry:
        console.print(f"[red]Error not found:[/red] {args[0]}")
        console.print("  [dim]Try a fingerprint prefix, full fingerprint, or short ID[/dim]")
        return True

    st = entry.get("status", "?")
    sev = entry.get("severity", "?")
    sc = _STATUS_COLORS.get(st, "white")
    svc = _SEVERITY_COLORS.get(sev, "white")

    lines = [
        f"  [bold]ID:[/bold]              {entry.get('id', '?')}",
        f"  [bold]Fingerprint:[/bold]     {entry.get('fingerprint', '?')}",
        f"  [bold]Error Type:[/bold]      {entry.get('error_type', '?')}",
        f"  [bold]Component:[/bold]       {entry.get('component', '?')}",
        f"  [bold]Severity:[/bold]        [{svc}]{sev}[/{svc}]",
        f"  [bold]Status:[/bold]          [{sc}]{st}[/{sc}]",
        f"  [bold]Count:[/bold]           {entry.get('count', 0)}",
        f"  [bold]First Seen:[/bold]      {entry.get('first_seen', '?')}",
        f"  [bold]Last Seen:[/bold]       {entry.get('last_seen', '?')}",
        f"  [bold]Log Path:[/bold]        {entry.get('log_path', 'N/A') or 'N/A'}",
        f"  [bold]Fix Status:[/bold]      [{_FIX_STATUS_COLORS.get(entry.get('source_fix_status', 'none'), 'white')}]{entry.get('source_fix_status', 'none')}[/{_FIX_STATUS_COLORS.get(entry.get('source_fix_status', 'none'), 'white')}]",
    ]
    if entry.get("suppress_reason"):
        lines.append(f"  [bold]Suppress Reason:[/bold] {entry['suppress_reason']}")
    lines += ["", "  [bold]Message:[/bold]", f"    {entry.get('message', '?')}",
              "", "  [bold]Normalized:[/bold]", f"    {entry.get('normalized_message', '?')}"]

    console.print(Panel("\n".join(lines), title=f"Error Detail - {entry.get('id', '?')}", style="bold"))
    return True


def _cmd_suppress(console, args: list) -> bool:
    """Mark error as suppressed with optional reason."""
    if not args:
        console.print("[red]Missing error ID or fingerprint[/red]")
        console.print("Usage: drone @trigger errors suppress <id_or_fingerprint> [reason]")
        return True

    entry = _find_by_id_or_fp(args[0])
    if not entry:
        console.print(f"[red]Error not found:[/red] {args[0]}")
        return True

    reason = " ".join(args[1:]) if len(args) > 1 else "No reason provided"
    fp = entry.get("fingerprint", args[0])

    if update_status(fp, "suppressed", reason):
        logger.info(f"[ERRORS] Suppressed {entry.get('id', '?')} ({fp[:12]}): {reason}")
        console.print(f"[yellow]Suppressed[/yellow] error {entry.get('id', '?')} ({fp[:12]})")
        console.print(f"  Reason: {reason}")

        # Phase 5: Source fix pipeline - notify source branch
        # Reload entry to get updated suppress_reason
        updated_entry = get_entry(fp)
        if updated_entry:
            if _send_source_fix_email(updated_entry):
                update_source_fix_status(fp, "fix_requested")
                console.print(f"  [cyan]Source fix email sent to @{updated_entry.get('component', '?').lower()}[/cyan]")
            else:
                update_source_fix_status(fp, "pending_fix")
                console.print(f"  [dim]Source fix email could not be sent (status: pending_fix)[/dim]")
    else:
        console.print(f"[red]Failed to suppress error[/red] {args[0]}")
    return True


def _cmd_resolve(console, args: list) -> bool:
    """Mark error as resolved."""
    if not args:
        console.print("[red]Missing error ID or fingerprint[/red]")
        console.print("Usage: drone @trigger errors resolve <id_or_fingerprint>")
        return True

    entry = _find_by_id_or_fp(args[0])
    if not entry:
        console.print(f"[red]Error not found:[/red] {args[0]}")
        return True

    fp = entry.get("fingerprint", args[0])
    if update_status(fp, "resolved"):
        logger.info(f"[ERRORS] Resolved {entry.get('id', '?')} ({fp[:12]})")
        console.print(f"[green]Resolved[/green] error {entry.get('id', '?')} ({fp[:12]})")
    else:
        console.print(f"[red]Failed to resolve error[/red] {args[0]}")
    return True


def _cmd_clear_resolved(console, args: list) -> bool:
    """Purge old resolved entries. Optional --days=N (default 7)."""
    days = int(_parse_args(args).get("days", "7"))
    removed = clear_resolved(days=days)
    if removed > 0:
        logger.info(f"[ERRORS] Cleared {removed} resolved entries older than {days} days")
        console.print(f"[green]Cleared {removed} resolved error(s)[/green] older than {days} days")
    else:
        console.print(f"[dim]No resolved errors older than {days} days to clear[/dim]")
    return True


def _cmd_stats(console, args: list) -> bool:
    """Show summary statistics and circuit breaker state."""
    stats = get_stats()
    cb = get_circuit_breaker_status()

    console.print("Error Registry Statistics")
    console.print()
    console.print(f"  [bold]Total errors:[/bold]  {stats['total']}")
    console.print()

    for label, data, color_fn in [
        ("By Status", stats["by_status"], lambda k: _STATUS_COLORS.get(k, "white")),
        ("By Component", stats["by_component"], lambda _: "white"),
        ("By Severity", stats["by_severity"], lambda k: _SEVERITY_COLORS.get(k, "white")),
    ]:
        if data:
            console.print(f"  [bold]{label}:[/bold]")
            for key, count in sorted(data.items()):
                c = color_fn(key)
                console.print(f"    [{c}]{key:<15}[/{c}] {count}")
            console.print()

    cb_st = cb.get("state", "unknown")
    cc = _CB_COLORS.get(cb_st, "white")
    console.print("  [bold]Circuit Breaker:[/bold]")
    console.print(f"    State:         [{cc}]{cb_st}[/{cc}]")
    console.print(f"    Cooldown:      {cb.get('cooldown_seconds', 0)}s")
    console.print(f"    Recent errors: {cb.get('recent_error_count', 0)}")
    console.print()
    return True


def _cmd_circuit_breaker(console, args: list) -> bool:
    """Show or reset the circuit breaker."""
    if args and args[0] == "reset":
        circuit_breaker_reset()
        logger.info("[ERRORS] Circuit breaker manually reset to closed")
        console.print("[green]Circuit breaker reset to CLOSED[/green]")
        console.print("  All dispatch now allowed")
        return True

    cb = get_circuit_breaker_status()
    cb_st = cb.get("state", "unknown")
    cc = _CB_COLORS.get(cb_st, "white")

    console.print("Circuit Breaker Status")
    console.print()
    console.print(f"  State:           [{cc}]{cb_st}[/{cc}]")
    console.print(f"  Cooldown:        {cb.get('cooldown_seconds', 0)}s")
    console.print(f"  Recent errors:   {cb.get('recent_error_count', 0)}")
    console.print(f"  Summary sent:    {cb.get('summary_sent', False)}")
    console.print()

    if cb_st == "closed":
        console.print("  [dim]Normal operation - all dispatch allowed[/dim]")
    elif cb_st == "open":
        opened_at = cb.get("opened_at", 0)
        cooldown = cb.get("cooldown_seconds", 0)
        if opened_at > 0:
            remaining = max(0, cooldown - int(time.time() - opened_at))
            console.print(f"  [red]Dispatch paused[/red] - {remaining}s remaining until half-open")
        else:
            console.print("  [red]Dispatch paused[/red]")
        console.print()
        console.print("  [dim]Run 'drone @trigger errors circuit-breaker reset' to force close[/dim]")
    elif cb_st == "half_open":
        console.print("  [yellow]Testing recovery[/yellow] - one probe dispatch allowed")
        console.print()
        console.print("  [dim]Run 'drone @trigger errors circuit-breaker reset' to force close[/dim]")

    return True


if __name__ == "__main__":
    from aipass.cli.apps.modules import console

    if len(sys.argv) == 1 or sys.argv[1] in ['--help', '-h', 'help']:
        print_help()
        sys.exit(0)

    handle_command("errors", sys.argv[1:])
