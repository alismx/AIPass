# DPLAN-003 Working Directory

Research, mapping, and planning files for "AIPass as Operating System."

Parent plan: `AIPass/DPLAN-003_aipass_as_operating_system_2026-03-13.md`

## Scope

**In scope:** `src/aipass/` branches only (drone, seedgo, prax, cli, flow, ai_mail, api, trigger, spawn, devpulse, backup, daemon, memory).

**Out of scope:** `src/commons/`, `src/skills/` — these are separate and not part of this refactor.

## Files

| File | Purpose | Status |
|------|---------|--------|
| `registry_discovery_map.md` | Every find_registry() call in src/aipass/ | Done |
| `portability_audit.md` | Full investigation results (session 24) | Done |
| `credential_model.md` | Registry credential design (UUID now, macaroons later) | Active |
| `registry_refactor_plan.md` | Shared function design, migration steps | Pending |
| `aipass_init_spec.md` | What `aipass init` creates, CLI design, templates | Pending |
| `drone_help_spec.md` | `drone aipass help` module design | Pending |
