# FPLAN-0004 - [framework] Backup System — port to AIPass repo

**Created**: 2026-03-06
**Branch**: /home/aipass/aipass_business/AIPass
**Status**: Active
**Type**: Standard Plan

---

## What Are Flow Plans?

Flow Plans (FPLANs) are for **BUILDING** - autonomous construction of systems, features, modules.

**This is NOT for:**
- Research or exploration (use agents directly)
- Quick fixes (just do it)
- Discussion or planning (that happens before creating the FPLAN)

**This IS for:**
- Building features or modules
- Single focused construction tasks
- Sub-plans within a master plan

---

## When to Use This vs Master Plan

| This (Default) | Master Plan |
|----------------|-------------|
| Single focused task | 3+ phases, complex build |
| Self-contained | Roadmap + multiple sub-plans |
| Quick build | Multi-session project |
| One phase of a master | Entire branch/system build |

**Need a master plan?** `drone @flow create "subject" master`

---

## Branch Directory Structure

Use dedicated directories - don't scatter files:

| Directory | Purpose |
|-----------|---------|
| `apps/` | Code (modules/, handlers/) |
| `tests/` | All test files |
| `tools/` | Utility scripts |
| `artifacts/` | Agent outputs |
| `docs/` | Documentation |

---

## Critical: Branch Manager Role

**You are the ORCHESTRATOR, not the builder.**

Your 200k context is precious. Burning it on file reads and code writing risks compaction during autonomous work. Agents have clean context - use them for ALL building.

| You Do (Orchestrator) | Agents Do (Builders) |
|-----------------------|----------------------|
| Create plans | Write code |
| Give instructions | Run tests |
| Review output | Read/modify files |
| Course correct | Research/exploration |
| Update memories | Heavy lifting |
| Send status emails | Single-task execution |

**Pattern:** Instruct agent → Wait for completion → Review output → Next step

---

## Seek Branch Expertise

Don't figure everything out alone. Other branches are domain experts - ask them first.

**Before building anything that touches another branch's domain:**
```bash
ai_mail send @branch "Question: [topic]" "I'm working on X and need guidance on Y. What's the best approach?"
```

**Common examples:**
- Building something with email? Ask @ai_mail how delivery works
- Need routing or @ resolution? Ask @drone
- Unsure about standards? Ask @seed for reference code
- Need persistent storage or search? Ask @memory_bank
- Event-driven behavior? Ask @trigger about their event system
- Dashboard integration? Ask @devpulse about update_section()

They have deep memory on their systems. A 1-email question saves you hours of guessing.

---

## Notepad

Keep `notepad.md` in your branch directory as a shared scratchpad during the build. Use it for:
- **Status updates** - Quick progress lines so Patrick can glance without asking
- **Questions for Patrick** - Non-urgent questions that can wait for his next visit
- **Notes to self** - Decisions made, things to revisit, gotchas discovered

Update it as you work - lightweight, not formal. Patrick checks it when he wants to, skips it when he's busy.

---

## Command Reference

When unsure about syntax, use `--help`:

```bash
# Flow - Plan management
drone @flow create . "subject"         # Create plan (. = current dir)
drone @flow close FPLAN-XXXX           # Close plan
drone @flow list                       # List active plans
drone @flow --help                     # Full help

# Seed - Quality gates
drone @seed checklist <file>           # 10-point check on file
drone @seed audit @branch              # Full branch audit
drone @seed --help                     # Full help

# AI_Mail - Status updates
drone @ai_mail send @dev_central "Subject" "Message"
drone @ai_mail --help                  # Full help

# Discovery
drone systems                          # All available modules
drone list @branch                     # Commands for branch
```

---

## Planning Phase

### Goal
Port the internal Backup System (`/home/aipass/aipass_core/backup_system/`) into the AIPass public repo at `src/aipass/backup/`. Working backup with snapshot mode, versioned mode, Google Drive sync (optional), dry-run support, and 90+ ignore patterns. Same approach as FPLAN-0003 (Memory Bank) — rewire, don't rebuild.

### Approach
1. Copy all source files from internal backup_system/apps/ into src/aipass/backup/apps/
2. Deploy parallel agents to adapt imports (remove prax/cli/sys.path, use relative imports, make Google Drive optional)
3. Fix hardcoded paths to use `Path(__file__).resolve().parents[N]`
4. Verify no internal references remain

### Reference Documents
- Source: `/home/aipass/aipass_core/backup_system/apps/` (entry point + 4 modules + ~20 handlers)
- Pattern: FPLAN-0003 (Memory Bank port) — identical approach
- Architecture: 3-layer (apps/backup.py → modules/ → handlers/)

---

## Agent Preparation (Before Deploying)

Agents can't work blind. They need context before they build.

**Your Prep Work (as orchestrator):**
1. [ ] Know where agent will work (branch path, key directories)
2. [ ] Identify files agent needs to reference or modify
3. [ ] Gather any specs, planning docs, or examples to include
4. [ ] Prepare COMPLETE instructions (agents are stateless)

**Agent's First Task (context building):**
- Agent should explore/read relevant files BEFORE writing code
- "First, read X and Y to understand the current structure"
- "Look at Z for the pattern to follow"
- Context-first, build-second

**What Agents DON'T Have:**
- No prior conversation history
- No memory files loaded automatically
- No knowledge of other branches
- Only what you put in their instructions

**Your instructions determine success - be thorough and specific.**

---

## Agent Instructions Template
```
You are working at [BRANCH_PATH].

TASK: [Specific single task]

CONTEXT:
- [What they need to know]
- Reference: [planning docs, existing code to study]
- First, READ the relevant files to understand current structure

DELIVERABLES:
- [Specific file or output expected]
- Tests → tests/
- Reports/logs → artifacts/reports/ or artifacts/logs/

CONSTRAINTS:
- Follow Seed standards (3-layer architecture)
- Do NOT modify files outside your task scope
- CROSS-BRANCH: Never modify other branches' files unless explicitly authorized by DEV_CENTRAL
- 2-ATTEMPT RULE: If something fails twice, note the issue and move on
- Do NOT go down rabbit holes debugging

WHEN COMPLETE:
- Verify code runs without syntax errors
- List files created/modified
- Note any issues encountered (with what was attempted)
```

---

## Execution Log

### 2026-03-06
- [x] Created FPLAN-0004
- [x] Agent deployed for: investigate backup_system structure (returned full report)
- [x] Created directory structure: src/aipass/backup/apps/{modules,handlers/{config,models,operations,utils,json,diff,reporting},json_templates/default,extensions,plugins}
- [x] Copied 42 files from internal backup_system
- [x] Agent 1 deployed: adapt 5 modules + entry point (completed — all imports fixed)
- [x] Agent 2 deployed: adapt 20 handler files (completed — all imports fixed)
- [x] Manual fix: handlers/__init__.py cross-branch guard removed (incompatible with public repo paths)
- [x] Manual fix: removed unused imports in backup_core.py (load_json, save_json, temporarily_writable, module-level logger.info)
- [x] Verified: zero remaining internal imports (prax, cli, sys.path, aipass_core, backup_system.apps)
- [ ] Memories updated

**Log Pattern:** Task → Agent → Outcome → Quality check → Next

**If production stops (critical blocker):**
```bash
drone @ai_mail send @dev_central "PRODUCTION STOPPED: FPLAN-0004" "Issue: [description]. Attempted: [what was tried]. Awaiting guidance."
```

---

## Notes

- Same port-by-rewiring pattern as Memory Bank (FPLAN-0003): copy files, adapt imports, verify
- Google Drive deps (google-api-python-client, google-auth-oauthlib) made optional via try/except
- drive_sync_client.py already had Google API imports wrapped — just fixed internal path refs
- handlers/__init__.py had cross-branch security guard that checked for `/backup_system/` in caller path — incompatible with new `/backup/` path, replaced with simple package init
- JSON runtime data dir changed from `backup_system_json/` to `backup_json/` (relative to backup root)
- Timestamps file moved to `backup_data/backup_timestamps.json`
- Entry point renamed from `backup_system.py` to `backup.py`
- All `header()` calls from cli module replaced with local `_header()` helpers

---

## Completion Checklist

### Before Closing

- [ ] All goals achieved
- [ ] Agent output reviewed and verified
- [ ] Seed checklist on new code: `drone @seed checklist <file>`
- [ ] Branch memories updated:
  - [ ] `BRANCH.local.json` - session/work log
  - [ ] `BRANCH.observations.json` - patterns learned (if any)
- [ ] README.md updated (if build changed status/capabilities)
- [ ] Status email sent to DEV_CENTRAL:
  ```bash
  drone @ai_mail send @dev_central "FPLAN-0004 Complete" "Summary of what was done, any issues, outcomes"
  ```

**Completion Order:** Memories → README → Email (README before email - don't report complete with stale docs)

### Definition of Done
- All backup_system files ported to src/aipass/backup/ with working imports
- Zero references to internal paths (prax, cli, aipass_core, sys.path hacks)
- Google Drive integration optional (graceful degradation when deps missing)
- JSON templates preserved for module initialization
- Entry point (backup.py) routes commands to all 4 modules

---

## Close Command

When all boxes checked:
```bash
drone @flow close FPLAN-0004
```
