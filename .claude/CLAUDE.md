# AIPass Framework

Orchestration framework for autonomous AI agent ecosystems.

## Structure

- `src/aipass/` — All modules live here
- 10 modules: drone, seedgo, prax, cli, flow, ai_mail, api, trigger, spawn, devpulse
- 3-layer architecture per module: `apps/branch.py` (entry) + `apps/modules/` (logic) + `apps/handlers/` (impl)
- `AIPASS_REGISTRY.json` — Branch registry at repo root

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
- Each module has `.trinity/` (passport, local, observations) for identity/memory
- Each module has `.aipass/branch_system_prompt.md` for AI context injection
- Tests: `pytest` from repo root
- Branch prompt hook loads context from CWD's `.aipass/branch_system_prompt.md`

## Dev Rules

- Never bare imports (`from flow.apps...`) — always `from aipass.flow.apps...`
- Test in Docker for isolation verification (localhost:8080 code-server)
- `pyproject.toml` defines CLI entry points: `drone`, `seedgo`
