# DevPulse

**Purpose:** Dev notes and status tracking for AIPass projects
**Module:** `aipass.devpulse`
**Status:** Building

---

## Overview

DevPulse tracks development notes, plans, and project status across an AIPass ecosystem. It provides a shared notation layer where both humans and agents can log issues, todos, and progress — giving visibility into what's happening without requiring meetings or status emails.

### How It Works
- **Entry Point:** `apps/devpulse.py`
- **Pattern:** Auto-discovers modules in `apps/modules/` with `handle_command()` and routes commands

---

## Architecture

```
devpulse/
├── apps/
│   ├── devpulse.py        # Entry point (auto-discovery + routing)
│   ├── modules/           # Business logic
│   ├── handlers/          # Implementation
│   └── plugins/           # Extensions
├── devpulse_json/         # JSON storage
├── docs/
├── tests/
└── README.md
```

---

## Commands

```bash
drone @devpulse --help     # Show available commands
```

*Modules are being built out — commands will appear as they ship.*

---

## Python Usage

```python
from aipass.devpulse.apps.devpulse import discover_modules, route_command

# Discover available sub-modules
modules = discover_modules()

# Route a command
route_command("status", [], modules)
```

---

## Integration Points

### Depends On
- `aipass.prax` — Logging
- `aipass.cli` — Display formatting

### Provides To
- All modules — dev notes, plan tracking, project status
