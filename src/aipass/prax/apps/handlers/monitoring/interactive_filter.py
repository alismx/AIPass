#!/home/aipass/.venv/bin/python3

# META DATA HEADER
# Name: interactive_filter.py - Command Parser and Filter State
# Version: 0.1.0

"""Parse commands and maintain filtering state"""

from dataclasses import dataclass, field
from typing import Set, List, Tuple, Optional

@dataclass
class FilterState:
    """Current monitoring filter state"""
    watched_branches: Set[str] = field(default_factory=set)
    show_all: bool = False
    show_errors: bool = True
    show_warnings: bool = True
    show_info: bool = False
    verbosity: str = 'low'

    def is_watching(self, branch: str) -> bool:
        """Check if branch is being watched.

        Handles subagent labels like 'DEV_CENTRAL AGENT' by also checking
        the base branch name (without ' AGENT' suffix).
        """
        if self.show_all:
            return True
        if not self.watched_branches:
            return True
        if branch in self.watched_branches:
            return True
        # Check base branch name for subagent labels (e.g. 'DEV_CENTRAL AGENT' → 'DEV_CENTRAL')
        if branch.endswith(' AGENT'):
            return branch[:-6] in self.watched_branches
        return False

def parse_command(cmd: str) -> Tuple[Optional[str], List[str]]:
    """Parse user command into action and arguments

    Supported commands:
        watch <branch>   - Watch specific branch(es)
        watch all        - Watch all branches
        watch errors     - Only show errors
        filter <level>   - Set verbosity level (high/low)
        monitor errors   - Add errors to current view
        monitor warnings - Add warnings to current view
        status          - Show current filter state
        help            - Show help text
        quit/exit       - Stop monitoring
        clear           - Reset filters to quiet mode

    Args:
        cmd: Raw command string from user input

    Returns:
        Tuple of (command_name, arguments) or (None, []) for empty/invalid input

    Example:
        parse_command("watch seed") -> ("watch", ["seed"])
        parse_command("filter high") -> ("filter", ["high"])
        parse_command("") -> (None, [])
    """
    if not cmd:
        return None, []

    parts = cmd.strip().split()
    if not parts:
        return None, []

    command = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []

    # Normalize command aliases
    if command in ['exit', 'q']:
        command = 'quit'

    return command, args

def apply_filter(state: FilterState, command: str, args: List[str]):
    """Update filter state based on command

    Modifies the FilterState object in-place based on the command.

    Commands:
        watch <branch>  - Exclusive watch (clears previous filters)
        watch all       - Watch all branches
        watch errors    - Only show errors
        filter <level>  - Set verbosity (high/low)
        monitor errors  - Add errors to current view (inclusive)
        monitor warnings - Add warnings to current view (inclusive)
        clear           - Reset to quiet mode

    Args:
        state: FilterState object to modify
        command: Command name (from parse_command)
        args: Command arguments (from parse_command)
    """
    if command == 'watch':
        # Exclusive watch (clear previous)
        if not args or args[0] == 'all':
            state.show_all = True
            state.watched_branches.clear()
            state.show_info = True
        elif args[0] == 'errors':
            state.show_errors = True
            state.show_warnings = False
            state.show_info = False
        else:
            # Watch specific branches
            state.show_all = False
            state.watched_branches = set(b.upper() for b in args)
            state.show_info = True

    elif command == 'filter':
        # Set verbosity level
        if args and args[0] in ['high', 'low']:
            state.verbosity = args[0]

    elif command == 'monitor':
        # Inclusive monitor (add to current)
        if args and args[0] == 'errors':
            state.show_errors = True
        elif args and args[0] == 'warnings':
            state.show_warnings = True

    elif command == 'verbosity':
        # Legacy support - redirect to filter
        if args and args[0] in ['high', 'low']:
            state.verbosity = args[0]

    elif command == 'clear':
        # Reset to quiet mode
        state.show_all = False
        state.watched_branches.clear()
        state.show_info = False
        state.show_errors = True
        state.show_warnings = True
        state.verbosity = 'low'

def should_display_event(event_type: str, branch: str, level: str, state: FilterState, message: str = '') -> bool:
    """Determine if event should be displayed based on filters

    Args:
        event_type: Type of event (log, file, command, etc.)
        branch: Branch name
        level: Event level (error, warning, info, debug)
        state: Current FilterState
        message: Event message content (for noise filtering)

    Returns:
        True if event should be displayed
    """
    # Check branch filter
    if not state.is_watching(branch):
        return False

    # File, command, and agent events always show when watching a branch
    # (level filter only applies to log events)
    if event_type in ['file', 'command', 'agent']:
        return True

    # Check level filter (for log events only)
    if level == 'error' and not state.show_errors:
        return False
    if level == 'warning' and not state.show_warnings:
        return False
    if level == 'info' and not state.show_info:
        return False

    # Verbosity filter - skip noise patterns when verbosity is 'low'
    if state.verbosity == 'low' and level == 'info' and message:
        noise_patterns = [
            'Discovered module:',
            'Module loaded:',
            'Initializing',
            'Configuration loaded',
            'Registry loaded',
            'Data loaded',
            'check complete:',
            'Running ',  # "Running X standard check"
        ]
        for pattern in noise_patterns:
            if pattern in message:
                return False

    return True

def get_status_text(state: FilterState) -> str:
    """Get current filter status as formatted text

    Args:
        state: Current FilterState

    Returns:
        Multi-line string showing current filter configuration

    Example:
        >>> state = FilterState(watched_branches={'SEED', 'CLI'})
        >>> print(get_status_text(state))
        Current Monitoring Status:
          Branches: SEED, CLI
          Levels: errors, warnings
          Verbosity: low
    """
    lines = ["Current Monitoring Status:"]

    # Branch filter
    if state.show_all:
        lines.append("  Branches: ALL")
    elif state.watched_branches:
        branches = ", ".join(sorted(state.watched_branches))
        lines.append(f"  Branches: {branches}")
    else:
        lines.append("  Branches: (quiet mode - errors/warnings only)")

    # Level filter
    levels = []
    if state.show_errors:
        levels.append("errors")
    if state.show_warnings:
        levels.append("warnings")
    if state.show_info:
        levels.append("info")

    if levels:
        lines.append(f"  Levels: {', '.join(levels)}")
    else:
        lines.append("  Levels: (none - all filtered)")

    # Verbosity
    lines.append(f"  Verbosity: {state.verbosity}")

    return "\n".join(lines)


def get_help_text() -> str:
    """Get help text for interactive commands"""
    return """
Available Commands:
  watch <branch>    - Watch specific branch(es) (comma-separated)
  watch all         - Watch all branches
  watch errors      - Only show errors
  filter <level>    - Set verbosity (high/low)
  monitor errors    - Add errors to current view
  monitor warnings  - Add warnings to current view
  clear             - Reset to quiet mode
  status            - Show current filters
  help              - Show this help
  quit/exit         - Stop monitoring
"""
