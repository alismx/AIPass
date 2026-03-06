
"""
EXAMPLE: How to integrate log_watcher into monitor_module.py

This is a reference implementation showing the minimal changes needed
to add log monitoring to monitor_module.py's handle_command() function.

Copy the relevant sections into monitor_module.py as needed.
"""

import sys
from pathlib import Path
from typing import List

from aipass.prax.apps.modules.logger import system_logger as logger
from aipass.cli.apps.modules import console, header, success, error, warning

# Import monitoring components
from aipass.prax.apps.handlers.monitoring import (
    start_log_watcher,        # NEW: Log watcher integration
    stop_log_watcher,         # NEW: Log watcher cleanup
    is_log_watcher_active,    # NEW: Status check
    MonitoringQueue,
    MonitoringEvent,
    print_event,
    FilterState,
    should_display_event,
)

# Global state
_log_observer = None
_event_queue = None


def handle_command(command: str, args: List[str]) -> bool:
    """
    Example handle_command with log watcher integration

    This shows the minimal changes to add real-time log monitoring
    to the existing monitor_module.py structure.
    """
    if command != 'monitor':
        return False

    global _log_observer, _event_queue

    logger.info(f"Starting unified monitoring (args: {args})")

    # Display header
    console.print()
    header("PRAX Mission Control - Unified Monitoring")
    console.print()

    # Initialize event queue
    _event_queue = MonitoringQueue()
    console.print("[green]✓ Event queue initialized[/green]")

    # Start log watcher - NEW INTEGRATION
    try:
        _log_observer = start_log_watcher(_event_queue)
        console.print("[green]✓ Log watcher started[/green]")
        console.print(f"[dim]  Monitoring: system_logs/*.log[/dim]")
    except Exception as e:
        error(f"Failed to start log watcher: {e}")
        logger.error(f"Log watcher startup failed: {e}")
        return False

    console.print()
    console.print("[yellow]Monitoring active - type 'quit' to exit[/yellow]")
    console.print()

    # Initialize filter state
    filter_state = FilterState()

    # Parse branch filters from args
    if args:
        branches = args[0].split(',') if args[0] != 'all' else []
        if branches:
            filter_state.watched_branches = {b.strip().upper() for b in branches}
            console.print(f"[cyan]Filtering branches: {', '.join(filter_state.watched_branches)}[/cyan]")
            console.print()

    try:
        # Main event loop
        while True:
            # Dequeue next event (with timeout to allow Ctrl+C)
            event = _event_queue.dequeue(timeout=0.5) if _event_queue else None

            if event:
                # Apply filters
                if should_display_event(event.event_type, event.branch, event.level, filter_state):

                    # Handle command separator events
                    if event.event_type == 'command':
                        console.print(f"\n[bold green]{event.message}[/bold green]\n")

                    # Handle log events
                    elif event.event_type == 'log':
                        # Format timestamp
                        timestamp = event.timestamp.strftime('%H:%M:%S')

                        # Branch column (right-aligned, fixed width)
                        branch_col = f"[{event.branch:>8}]"

                        # Color by level
                        level_colors = {
                            'error': 'red',
                            'warning': 'yellow',
                            'info': 'white',
                            'debug': 'dim',
                        }
                        color = level_colors.get(event.level, 'white')

                        # Display event
                        console.print(
                            f"[dim]{timestamp}[/dim] "
                            f"[cyan]{branch_col}[/cyan] "
                            f"[{color}]{event.message}[/{color}]"
                        )

            # Check for keyboard input (simplified - use proper input handling)
            # TODO: Add interactive command handling here

    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping monitoring...[/yellow]")

    finally:
        # Cleanup
        if _log_observer:
            stop_log_watcher()
            console.print("[green]✓ Log watcher stopped[/green]")

        if _event_queue:
            _event_queue.stop()
            console.print("[green]✓ Event queue stopped[/green]")

    console.print()
    success("Monitoring stopped")

    return True


def example_with_interactive_commands():
    """
    Example showing interactive command handling

    This is a more complete version with command input handling.
    Requires threading to read both events and keyboard input.
    """
    import threading
    import select

    def input_handler(running_flag):
        """Thread for reading keyboard input"""
        while running_flag[0]:
            # Use select for non-blocking input on Unix
            if select.select([sys.stdin], [], [], 0.5)[0]:
                try:
                    user_input = sys.stdin.readline().strip()

                    if user_input in ['quit', 'exit']:
                        running_flag[0] = False
                    elif user_input == 'help':
                        console.print("\n[bold]Commands:[/bold]")
                        console.print("  help   - Show this help")
                        console.print("  status - Show monitoring status")
                        console.print("  quit   - Exit monitoring\n")
                    elif user_input == 'status':
                        console.print(f"\n[bold]Status:[/bold]")
                        console.print(f"  Log watcher: {'active' if is_log_watcher_active() else 'inactive'}")
                        console.print(f"  Queue size: {_event_queue.size() if _event_queue else 0}\n")

                except Exception:
                    pass

    # Running flag for threads
    running = [True]

    # Start input handler thread
    input_thread = threading.Thread(target=input_handler, args=(running,))
    input_thread.daemon = True
    input_thread.start()

    # Main event loop
    while running[0]:
        event = _event_queue.dequeue(timeout=0.5) if _event_queue else None
        if event:
            # Display event (same as above)
            pass


# Example of filter adjustment
def example_filter_adjustment():
    """Show how to dynamically adjust filters"""

    filter_state = FilterState()

    # Watch specific branches
    filter_state.watched_branches = {'SEED', 'FLOW', 'PRAX'}

    # Apply filter
    event = MonitoringEvent(
        priority=1,
        event_type='log',
        branch='SEED',
        level='error',
        message='ERROR: Something went wrong'
    )

    if should_display_event(event.event_type, event.branch, event.level, filter_state):
        print("Event passed filters")


if __name__ == '__main__':
    console.print("[bold cyan]Monitor Module Integration Examples[/bold cyan]")
    console.print()
    console.print("This file shows examples of integrating log_watcher.py")
    console.print("into monitor_module.py's handle_command() function.")
    console.print()
    console.print("[yellow]Key changes:[/yellow]")
    console.print("  1. Import start_log_watcher, stop_log_watcher")
    console.print("  2. Initialize MonitoringQueue")
    console.print("  3. Start log watcher with queue")
    console.print("  4. Main loop dequeues and displays events")
    console.print("  5. Cleanup on exit")
    console.print()
    console.print("[dim]See code above for full implementation details.[/dim]")
    console.print()
