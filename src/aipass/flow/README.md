# Flow

Plan lifecycle management for AIPass. Creates, tracks, closes, and archives numbered work plans (FPLANs) with registry-backed state, async post-processing, and cross-branch aggregation.

## Usage

### CLI (via drone)

```bash
drone @flow create . "Build authentication module"    # Create plan in current dir
drone @flow create /path/to "Migration task" master   # Master plan (multi-phase)
drone @flow close 42                                  # Close plan
drone @flow close --all                               # Close all open plans
drone @flow list                                      # List plans
drone @flow aggregate                                 # Aggregate plans across branches
drone @flow registry                                  # Registry health monitor
```

### Python

```python
from aipass.flow.apps.modules.create_plan import create_plan
from aipass.flow.apps.modules.close_plan import close_plan
from aipass.flow.apps.modules.list_plans import list_plans
from aipass.flow.apps.handlers.registry.load_registry import load_registry

# Load the plan registry
registry = load_registry()
```

## Architecture

```
flow/
├── apps/
│   ├── flow.py                  # Entry point (auto-discovers modules)
│   ├── modules/                 # Business logic
│   │   ├── create_plan.py       # Plan creation with template support
│   │   ├── close_plan.py        # Closure with async archival
│   │   ├── list_plans.py        # Plan listing and filtering
│   │   ├── restore_plan.py      # Plan recovery from backups
│   │   ├── registry_monitor.py  # Orphan detection, auto-healing
│   │   ├── aggregate_central.py # Cross-branch plan aggregation
│   │   └── post_close_runner.py # Background post-processing
│   └── handlers/                # Implementation details
│       ├── plan/                # Lifecycle, file ops, validation
│       ├── registry/            # Load, save, auto-heal
│       ├── template/            # Plan templates (default, master, proposal)
│       ├── dashboard/           # Status aggregation
│       ├── mbank/               # Memory bank archival
│       └── summary/             # AI-generated plan summaries
├── templates/                   # Plan template files
├── flow_json/                   # Configuration and registry data
└── tests/
```

## Plan Naming

Plans follow the convention `FPLAN-XXXX_topic_slug_YYYY-MM-DD.md` where XXXX is an auto-incrementing number.

## Dependencies

- `aipass.cli` — terminal formatting
- `aipass.prax` — structured logging
- `aipass.trigger` — error reporting (optional)

Last Updated: 2026-03-06
