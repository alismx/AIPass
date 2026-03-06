# AIPass Framework

Orchestration framework for autonomous AI agent ecosystems.

## Structure

- `src/aipass/` — All modules live here
- 10 modules: drone, seedgo, prax, cli, flow, ai_mail, api, trigger, spawn, devpulse
- 3-layer architecture per module: `apps/branch.py` (entry) + `apps/modules/` (logic) + `apps/handlers/` (impl)
- `AIPASS_REGISTRY.json` — Branch registry at repo root
- `.trinity/` per module — passport.json, local.json, observations.json (identity + memory)
- `.aipass/branch_system_prompt.md` per module — AI context injection

## Commands

```
drone systems                    # List registered modules/branches
drone @seedgo verify             # Verify standards packs installed
drone @seedgo audit aipass       # Run standards audit on repo
drone @module --help             # Module help
```

## Conventions

- All imports use pip namespace: `from aipass.{module}.apps.modules...`
- No hardcoded paths — use `Path(__file__).parents[N]` or registry lookups
- Tests: `pytest` from repo root
- Lint: `ruff check`
- Trinity Pattern is the memory dependency
- `pyproject.toml` defines CLI entry points: `drone`, `seedgo`

## Dev Rules

- Never bare imports (`from flow.apps...`) — always `from aipass.flow.apps...`
- Test in Docker for isolation verification (localhost:8080 code-server)
- No paths referencing `/home/aipass/` — that's Dev-Pass, not AIPass

## DevPulse

DevPulse (`src/aipass/devpulse/`) is the orchestration hub for this repo. It coordinates work across modules, tracks status, and manages dev notes. It is to AIPass what DEV_CENTRAL is to Dev-Pass.

## Current State

All modules in "building" status — imports rewired from Dev-Pass to pip namespace, not fully tested yet. MPLAN-001 (in Dev-Pass dev_central) tracks all component status.
