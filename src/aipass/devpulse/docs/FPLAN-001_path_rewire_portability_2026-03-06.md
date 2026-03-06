# FPLAN-001 - AIPass Path Rewire & Portability Fix (MASTER PLAN)

**Created**: 2026-03-06
**Branch**: src/aipass/devpulse
**Status**: Phase 5 (Final Verification)
**Type**: Master Plan (Multi-Phase)
**Reference**: DPLAN-047 (Path.home() Purge)

---

## Project Overview

### Goal
All 10 AIPass modules import cleanly on ANY system. Zero filesystem assumptions. Code runs after `pip install -e .` on Mac, Linux, CI runners, Docker — anywhere.

### CRITICAL: This is a Public Pip Package
AIPass is a PUBLIC pip package installable on ANY machine. There is NO `/home/aipass`. There is NO `aipass_core` directory. There is NO `.venv` at a known location. None of that exists outside Dev-Pass (the private source repo).

**Dev-Pass vs AIPass confusion is the #1 risk.** Code was ported from Dev-Pass where `/home/aipass` and `aipass_core` are real paths. Here, they are ghosts that crash on import.

### Only Valid Path Patterns
```python
# 1. Package-relative (where the code lives)
Path(__file__).resolve().parents[N]

# 2. Walk-up to repo root (finds AIPASS_REGISTRY.json)
def _find_repo_root() -> Path:
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "AIPASS_REGISTRY.json").exists():
            return parent
    return Path.cwd()

# 3. User's working directory
Path.cwd()
```

**Everything else is Dev-Pass baggage and MUST be removed or rewired.**

### Seedgo Standards Adjustment
Seedgo standards were built for Dev-Pass. Standards that don't align with public pip package reality MUST be adjusted:
- Shebang requirements: REMOVED (irrelevant for pip packages)
- `/home/aipass` reference paths in standards content: must be updated
- Any standard assuming filesystem structure beyond the package itself

### Reference Documentation
- `DPLAN-047_path_home_purge_portability_2026-03-06.md` (repo root)
- `docs/sub_agent_drops/path_home_audit.md` (full audit from session 1)
- `spawn/templates/agent.template/` (reference for correct patterns)

### Success Criteria
1. `pip install -e .` clean
2. All module top-level imports work (`from aipass.{module} import ...`)
3. `drone systems` shows 10 branches
4. `drone @seedgo verify` passes
5. `drone @seedgo audit aipass` runs without import crashes
6. Zero `Path.home()` or `/home/aipass` in functional code (comments/docstrings updated too)
7. Zero `aipass_core` references in functional code

---

## What We're Cleaning Up

This is a cleanup of Dev-Pass baggage. The code was ported from a private system that assumes `/home/aipass/aipass_core/` exists. We're making it universal.

### Fix Categories
1. **FUNCTIONAL** — `Path.home()`, `Path("/home/aipass/...")`, `aipass_core` in actual code logic → MUST fix or code crashes
2. **COMMENTS/DOCSTRINGS** — References to `/home/aipass` in documentation strings → Update to reflect package-relative reality
3. **STRING COMPARISONS** — Code checking for `aipass_core` in path parts → Adapt to new structure (`src/aipass/`)

### Fix Pattern

```python
# WRONG — Dev-Pass patterns (CRASH on any other system)
AIPASS_ROOT = Path.home() / "aipass_core"
ECOSYSTEM_ROOT = Path("/home/aipass")
SYSTEM_LOGS_DIR = Path("/home/aipass/system_logs")

# RIGHT — Package-relative
MODULE_ROOT = Path(__file__).resolve().parents[N]  # N = depth to module root

# RIGHT — Walk-up finder (proven in drone/seedgo)
def _find_repo_root() -> Path:
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "AIPASS_REGISTRY.json").exists():
            return parent
    return Path.cwd()

# RIGHT — Logs go in package-relative location
LOGS_DIR = Path(__file__).resolve().parents[3] / "logs"
```

---

## Phase Definitions

### Phase 1: Safe Modules (drone, cli, spawn, devpulse) — COMPLETE
**Goal:** Fix LOW severity modules
**Result:** drone (2 files), cli (12 files), spawn (4 files) — all verified clean
**Remaining:** drone/config.py has 1 Path.home() for registry (quick fix), cli/__init__.py has 1 string comparison (cosmetic)

### Phase 2: Prax — COMPLETE
**Goal:** `from aipass.prax import logger` works AND deeper handler imports don't crash
**Scope:** ~47 hits across functional code, comments, and string comparisons. Key files: introspection.py (14), branch_detector.py (8), monitor_module.py (6), setup.py (5), log_watcher.py (4)
**Result:** 16 files functional fixes + 17 files comments/docstrings updated. All imports verified.
**Critical:** Unblocks all other modules since they import prax

### Phase 3: Trigger + Flow — COMPLETE
**Goal:** Fix CRITICAL import-time crashes + all Dev-Pass path references
**Scope:** trigger (~50 hits), flow (~70 hits). CRITICAL: plan_file.py ECOSYSTEM_ROOT, registry_monitor.py ECOSYSTEM_ROOT
**Result:** Trigger 23 files fixed, flow 37 files fixed. All CRITICAL crashes resolved.
**Parallel:** Yes, 2 agents

### Phase 4: AI Mail + API — COMPLETE
**Goal:** Fix the heaviest modules
**Scope:** ai_mail (~80 hits), api (~70 hits). CRITICAL: ai_mail/registry/read.py, api/log_streamer.py
**Result:** ai_mail 37 files fixed, api 35 files fixed. All CRITICAL crashes resolved.
**Parallel:** Yes, 2 agents

### Phase 5: Seedgo Standards + Verification — IN PROGRESS
**Goal:** Fix seedgo's own Dev-Pass references + full system test
**Scope:** ~60 hits in seedgo standards content (reference strings pointing to /home/aipass/standards/). Remove shebang standard. Update all reference paths. Run full import + drone verification.
**Critical:** Seedgo standards must reflect the public pip package reality
**Progress:**
- Seedgo standards: 30 files updated (Dev-Pass reference paths)
- Shebang standard: CREATED (new SHEBANG check that fails files with shebangs)
- Shebangs stripped: 205 files cleaned codebase-wide
- Meta docs: aligned to match checker format
- 4 bare import violations: FIXED
- Full verification: All 10 modules import clean, `drone systems` works
- Remaining: Running `seedgo audit` for final violations

---

## Phase Tracking

### Phase 1: Safe Modules
- **Status:** COMPLETE
- **Agents:** 4 (drone, cli, spawn, devpulse)
- **Result:** All verified clean. Minor residual hits (drone config.py, cli __init__.py)

### Phase 2: Prax
- **Status:** COMPLETE
- **Agents:** 1
- **Result:** 16 files functional fixes, 17 files comments/docstrings. All imports verified.

### Phase 3: Trigger + Flow
- **Status:** COMPLETE
- **Agents:** 2
- **Result:** Trigger 23 files, flow 37 files. All CRITICAL import crashes fixed.

### Phase 4: AI Mail + API
- **Status:** COMPLETE
- **Agents:** 2
- **Result:** ai_mail 37 files, api 35 files. All CRITICAL import crashes fixed.

### Phase 5: Seedgo Standards + Verification
- **Status:** IN PROGRESS
- **Agents:** 2 (1 for seedgo cleanup, 1 for final verification)
- **Progress:** 30 seedgo files updated, shebang standard created, 205 shebangs stripped, 4 bare imports fixed. All 10 modules import clean. Remaining: final seedgo audit pass.

---

## Issues Log

| Phase | Issue | Severity | Attempted | Status |
|-------|-------|----------|-----------|--------|
| 2 | Prax agent lost during session compaction | LOW | Retry deployed | RESOLVED |
| 3 | trigger/plan_file.py ECOSYSTEM_ROOT crash | CRITICAL | Phase 3 | RESOLVED |
| 3 | flow/registry_monitor.py ECOSYSTEM_ROOT crash | CRITICAL | Phase 3 | RESOLVED |
| 4 | ai_mail/registry/read.py import crash | CRITICAL | Phase 4 | RESOLVED |
| 4 | api/log_streamer.py import crash | CRITICAL | Phase 4 | RESOLVED |
| 5 | 4 bare import violations (missing aipass. prefix) | HIGH | Phase 5 | RESOLVED |
| 5 | 205 files with shebangs (irrelevant for pip pkg) | MEDIUM | Phase 5 | RESOLVED |
| 5 | Seedgo standards referencing Dev-Pass paths | HIGH | Phase 5 | RESOLVED |
| 5 | Final seedgo audit for remaining violations | MEDIUM | In progress | OPEN |

---

## Notes

- **PUBLIC PIP PACKAGE** — This is the core principle. Zero filesystem assumptions. Works on any machine.
- **Dev-Pass confusion is the #1 risk** — All code was ported from a system where /home/aipass exists. Be vigilant.
- Seedgo standards built for Dev-Pass MUST be adjusted: shebang standard removed, reference paths updated
- Shebangs are IRRELEVANT for pip packages — don't waste time on them, focus on functional path violations
- Some modules reference Dev-Pass infrastructure (AI_CENTRAL, MEMORY_BANK, telegram) — guard or remove
- 2-attempt rule: if a fix breaks something, note it and move on
- Comments/docstrings referencing /home/aipass should be updated too — clean break from Dev-Pass

---

## Definition of Done
All 5 success criteria pass in Docker container.
