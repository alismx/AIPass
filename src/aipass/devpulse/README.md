# DEVPULSE

**Purpose:** Orchestration hub for AIPass public repo. Manages dev notes, DPLANs, system status dashboards. The DEV_CENTRAL of AIPass.
**Module:** `aipass.devpulse`
**Created:** 2026-03-06
**Last Updated:** 2026-03-06

---

## Overview

### What I Do
- Coordinate work across all 10 AIPass modules
- Track system health via seedgo audits and recon reports
- Manage DPLANs and development notes
- Test and wire modules in Docker container environment

### How I Work
- **Entry Point:** `apps/branch.py`
- **Pattern:** Auto-discovers modules in `apps/modules/` with `handle_command()` and routes commands

---

## Architecture

```
DEVPULSE/
├── apps/
│   ├── branch.py              # Entry point (auto-discovery + routing)
│   ├── modules/               # Business logic (empty, building out)
│   ├── handlers/              # Implementation
│   └── plugins/               # Extensions
├── .trinity/
│   ├── passport.json          # Identity
│   ├── local.json             # Session history
│   └── observations.json      # Collaboration patterns
├── .agent/                    # System metadata
├── .aipass/                   # Branch prompt context
├── artifacts/                 # Birth certificate
├── docs/
│   └── sub_agent_drops/       # Recon reports from sub-agents
├── tools/
│   └── verify_branch.py       # Template verification
├── devpulse_json/             # Branch JSON storage
├── tests/
├── DASHBOARD.local.json       # System status
├── flow.local.md              # Issues and todos
└── README.md
```

---

## Commands

*No modules built yet — commands will be added as modules are created.*

---

## Integration Points

### Depends On
- `aipass.prax` — Logger
- `aipass.cli` — Display formatting
- `aipass.seedgo` — Standards auditing

### Provides To
- All modules — orchestration coordination, system health tracking
