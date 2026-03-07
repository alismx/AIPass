# FPLAN-0005 - [framework] Daemon (assistant) — port to AIPass repo

**Created**: 2026-03-07
**Branch**: /home/aipass/aipass_business/AIPass
**Status**: Active
**Type**: Standard Plan

---

## Planning Phase

### Goal
Port the internal Assistant system (`/home/aipass/aipass_os/dev_central/assistant/`) into the AIPass public repo at `src/aipass/daemon/`. Rename from "assistant" to "daemon". Working scheduler with plugin system, scheduled tasks, activity monitoring, and cron-driven execution. Telegram integration optional. Same approach as FPLAN-0003/0004 — rewire, don't rebuild.

### Approach
1. Copy all source files from internal assistant/apps/ into src/aipass/daemon/apps/
2. Rename entry point from assistant.py to daemon.py
3. Deploy parallel agents to adapt imports (remove prax/cli/sys.path, use relative imports)
4. Make Telegram, ai_mail dispatch, and BRANCH_REGISTRY deps optional via try/except
5. Fix hardcoded paths to use `Path(__file__).resolve().parents[N]`
6. Verify no internal references remain

### Key Decisions
- **Rename**: assistant → daemon (Patrick approved)
- **Telegram**: Optional — wrap in try/except, graceful skip when unconfigured
- **ai_mail dispatch**: Optional — wake.py spawning won't work outside Dev-Pass, needs abstraction
- **BRANCH_REGISTRY**: Activity monitoring reads this — make it configurable, graceful fallback
- **Plugins**: Port all 5 plugins as examples, but they're Dev-Pass-specific — document as templates
- **filelock**: Only external dep (already lightweight)

### Reference Documents
- Source: `/home/aipass/aipass_os/dev_central/assistant/apps/` (entry point + 2 cron scripts + 4 modules + ~10 handlers + 5 plugins)
- Pattern: FPLAN-0003 (Memory Bank) and FPLAN-0004 (Backup System) — identical approach
- Architecture: 3-layer (apps/daemon.py → modules/ → handlers/)

### Investigation Summary
- **4 modules**: update, schedule, activity_report, actions
- **10 handlers** across 6 subdirs: actions/, json/, monitoring/ (3 files), schedule/ (3 files), telegram/, update/
- **5 plugins**: heartbeat, daily_audit, community_rotation, botfather_reminder, dev_central_monitor
- **2 cron scripts**: scheduler_cron.py, assistant_wakeup.py (renamed to daemon_wakeup.py)
- **External deps**: filelock only
- **Internal deps**: prax logger, cli console/header, ai_mail send_email_direct, api telegram_chat, BRANCH_REGISTRY.json
- **Tests**: 1 test file (test_actions_registry.py) with pytest

---

## Execution Log

### 2026-03-07
- [x] Created FPLAN-0005
- [x] Agent deployed for: investigate assistant structure (returned full report)
- [x] Created directory structure: src/aipass/daemon/apps/{modules,handlers/{actions,json,monitoring,schedule,telegram,update},plugins,extensions,json_templates/default}
- [x] Copied 41 files from internal assistant system (renamed assistant→daemon)
- [x] Agent 1 deployed: adapt 13 files (3 entry points + 4 modules + 5 plugins + plugin init) — completed
- [x] Agent 2 deployed: adapt 10 handler files — completed
- [x] Fixed standalone scripts (scheduler_cron.py, daemon_wakeup.py): changed relative imports to absolute package imports (standalone scripts can't use relative imports)
- [x] Fixed test file: removed sys.path manipulation, uses package imports
- [x] Fixed actions_registry.py: removed sys.path.insert in migrate_plugins, uses absolute package import
- [x] Fixed memory_health.py: removed hardcoded /home/aipass test path
- [x] Removed 3 remaining shebangs from conftest.py and handler __init__.py files
- [x] Cleaned unused imports (Path, sys, os, timedelta, Optional, Tuple) across modules
- [x] Verified: zero remaining internal imports (prax, cli, sys.path, aipass_core, aipass_os, assistant_json, ASSISTANT_ROOT)
- [ ] Memories updated

---

## Notes

- Same port-by-rewiring pattern as Memory Bank (FPLAN-0003) and Backup System (FPLAN-0004)
- Renamed assistant → daemon (Patrick approved the name)
- Standalone cron scripts (scheduler_cron.py, daemon_wakeup.py) can't use relative imports — fixed to use absolute package imports (aipass.daemon.apps.handlers.xxx)
- Telegram integration made optional via try/except + TELEGRAM_AVAILABLE flag
- ai_mail dispatch made optional via try/except + AI_MAIL_AVAILABLE flag
- Wake script path configurable via AIPASS_WAKE_SCRIPT env var
- BRANCH_REGISTRY path configurable via AIPASS_REGISTRY env var
- Daemon config path configurable via AIPASS_DAEMON_CONFIG env var
- filelock made optional (try/except, falls back to fcntl)
- handlers/__init__.py cross-branch guard removed (incompatible with public repo)
- JSON runtime data dir changed from assistant_json/ to daemon_json/
- Entry point renamed from assistant.py to daemon.py
- Wakeup script renamed from assistant_wakeup.py to daemon_wakeup.py
- All ASSISTANT.local.json refs changed to DAEMON.local.json
- Plugin system preserved — 5 example plugins ported as templates

---

## Completion Checklist

### Definition of Done
- All assistant files ported to src/aipass/daemon/ with working imports
- Entry point renamed from assistant.py to daemon.py
- Zero references to internal paths (prax, cli, aipass_core, aipass_os, sys.path hacks)
- Telegram integration optional (graceful degradation)
- ai_mail dispatch optional (abstracted for external use)
- Plugin system preserved with example plugins
- JSON templates preserved for module initialization
- Tests ported and passing

---

## Close Command

When all boxes checked:
```bash
drone @flow close FPLAN-0005
```
