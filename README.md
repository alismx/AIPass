[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

# AIPass

> **Building in public.** Active development — not a finished product. Expect breaking changes.

Orchestration framework for autonomous AI agent ecosystems. Command routing, symbolic addressing, standards enforcement, workflow management, and inter-agent messaging. Agents use `@branch` names that resolve at runtime instead of hard-coded paths. [Trinity Pattern](https://github.com/AIOSAI/Trinity-Pattern) provides the memory layer.

## Quick Start

```bash
git clone https://github.com/AIOSAI/AIPass.git
cd AIPass
./setup.sh
source .venv/bin/activate
```

Verify:

```bash
drone --help        # Command router
drone systems       # List registered modules and branches
```

## Core Concepts

### Drone — Command Router

Everything goes through `drone`. It resolves `@branch` names to paths and routes commands.

```bash
drone @seedgo audit aipass    # Run standards audit
drone @seedgo verify          # Check seedgo health
drone @spawn --help           # Show help for a branch
drone systems                 # List all registered modules
```

In Python:

```python
from aipass.drone.apps.modules.resolver import resolve_branch
from aipass.drone.apps.modules.registry import load_registry

path = resolve_branch("@drone")   # Resolve @name to path
registry = load_registry()        # Load full branch registry
```

### Seedgo — Standards Enforcement

Standards-based code auditor. Checks are organized into packs — the built-in `aipass` pack has 21 standards covering imports, architecture, naming, error handling, logging, and more.

```bash
drone @seedgo verify          # Health check
drone @seedgo list            # Show installed standard packs
drone @seedgo audit aipass    # Run the aipass standards pack
seedgo checklist aipass file  # Check a single file
```

### Symbolic Addressing

All modules register in `AIPASS_REGISTRY.json`. Drone resolves `@name` to paths at runtime — no hard-coded paths between modules.

## Architecture

All modules follow a 3-layer pattern:

```
src/aipass/<module>/
├── apps/
│   ├── <module>.py    # Entry point (what drone routes to)
│   ├── modules/       # Business logic
│   └── handlers/      # Implementation details
```

**10 modules:**

| Module | Purpose | Status |
|--------|---------|--------|
| `drone` | Command routing, `@branch` resolution | Working |
| `seedgo` | Standards enforcement, 21-standard pack | Working |
| `spawn` | Branch lifecycle — create, update, delete | Working |
| `cli` | Display formatting (Rich) | Working |
| `flow` | Workflow/plan management | Building |
| `ai_mail` | Inter-agent messaging, dispatch, wake | Building |
| `prax` | Logging and monitoring | Building |
| `api` | LLM access and model routing | Building |
| `trigger` | Event-driven automation | Building |
| `devpulse` | Orchestration hub (no code — coordination only) | Active |

## Docker

```bash
docker build -t aipass-test .
docker run -d -p 8080:8080 --name aipass-vscode aipass-test
```

Opens VS Code in browser at `http://localhost:8080` with AIPass pre-installed.

## Requirements

- Python 3.10+
- No external API keys required
- Dependencies: `rich`, `watchdog`

## License

MIT
