# Modules

Business logic for `DEVPULSE`. One module per command.

Modules orchestrate work by calling handlers. They are the public API of the branch — drone routes commands here.

## Modules

| Module | Purpose |
|---|---|
| `watchdog.py` | Directed wake system. Subcommands: `agent`, `timer`, `schedule`, `status`, `cancel`, `list`. Wakes devpulse reliably on agent exit, wall-clock time, or named duration. Replaces the old bash one-liner. |
| `feedback.py` | Cross-project feedback channel. `compose` / `inbox` handlers. Lets external projects report bugs/friction back to devpulse. |
