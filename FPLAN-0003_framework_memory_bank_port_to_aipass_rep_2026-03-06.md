# FPLAN-0003 - [framework] Memory Bank — port to AIPass repo

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
Port the internal Memory Bank system into `src/aipass/memory/` as a fully functional module. Every spawned branch should have working memory rollover, JSONL archival, and searchable archives out of the box. Vector storage (ChromaDB + sentence-transformers) as optional pip extra.

### What We're Porting
Source: `/home/aipass/MEMORY_BANK/` (~1,800 lines, 75+ files)

**Core (zero new deps — must ship):**
- `detector.py` — threshold detection via AIPASS_REGISTRY.json (600-line default)
- `extractor.py` — FIFO extraction of oldest sessions, backup-before-extract
- `line_counter.py` — metadata `current_lines` updates
- `json_handler.py` — atomic JSON read/write (temp file + rename)
- `archiver.py` — JSONL archive write + keyword search
- `rollover.py` module — orchestrates detect → extract → archive → update
- `search.py` module — keyword search over JSONL archives

**Optional (`pip install aipass[vectors]`):**
- `embedder.py` — sentence-transformers wrapper (all-MiniLM-L6-v2, 384-dim)
- `vector_store.py` — ChromaDB persistence, per-branch `.chroma/` dirs
- `vector_search.py` — semantic search with metadata filtering
- Graceful fallback to keyword search if deps not installed

**Not v1 (later):**
- Symbolic/fragmented memory (experimental, v0.3)
- Living template push system
- Dashboard integration (needs DevPulse)
- Central writer (needs AI_CENTRAL concept)
- Memory pool intake processing

### Key Decisions
- **passport.json** is the identity file name (not id.json)
- **`.trinity/`** stays as the memory directory name
- **AIPASS_REGISTRY.json** is used for branch discovery (same as internal BRANCH_REGISTRY.json)
- **No daemon** — auto-check on command execution or manual `drone @memory rollover`
- **3-layer architecture** — apps/memory.py → modules/ → handlers/
- **JSONL for base archive** — keyword search good enough for most users
- **ChromaDB optional** — subprocess isolation if Python version issues arise

### Spawn Template Updates
- Welcome session (session 0) in local.json on branch creation
- `.trinity/archive/` directory pre-created and empty
- Memory self-managing — agent updates files, rollover handles overflow

### Integration Points
- Drone: `drone @memory status|rollover|search` commands
- Spawn: post-spawn welcome memory
- Registry: reads AIPASS_REGISTRY.json for branch discovery
- Hooks: PreCompact already references memory context

### Reference Documents
- Internal Memory Bank: `/home/aipass/MEMORY_BANK/apps/` (source code)
- Internal rollover module: `/home/aipass/MEMORY_BANK/apps/modules/rollover.py` (676 lines)
- Internal detector: `/home/aipass/MEMORY_BANK/apps/handlers/monitor/detector.py`
- Internal extractor: `/home/aipass/MEMORY_BANK/apps/handlers/rollover/extractor.py`
- Spawn templates: `src/aipass/spawn/templates/agent.template/.trinity/`
- AIPass architecture: 3-layer pattern (apps → modules → handlers)

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
- [ ] Created FPLAN-0003
- [ ] Agent deployed for: [task]
- [ ] Agent completed: [outcome]
- [ ] Seed checklist passed: [file]
- [ ] Memories updated

**Log Pattern:** Task → Agent → Outcome → Quality check → Next

**If production stops (critical blocker):**
```bash
drone @ai_mail send @dev_central "PRODUCTION STOPPED: FPLAN-0003" "Issue: [description]. Attempted: [what was tried]. Awaiting guidance."
```

---

## Notes

[Working notes, issues encountered, decisions made]

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
  drone @ai_mail send @dev_central "FPLAN-0003 Complete" "Summary of what was done, any issues, outcomes"
  ```

**Completion Order:** Memories → README → Email (README before email - don't report complete with stale docs)

### Definition of Done
- `src/aipass/memory/` module exists with 3-layer architecture
- `drone @memory status` shows all branches and their memory file line counts
- `drone @memory rollover` detects and processes oversized files
- `drone @memory search "query"` returns keyword matches from JSONL archives
- Spawn creates branches with welcome session and empty archive dir
- All 13+ existing tests still pass
- New tests for memory module (detector, extractor, archiver, search)
- `pip install aipass[vectors]` adds ChromaDB + semantic search capability
- Memory module registered in AIPASS_REGISTRY.json

---

## Close Command

When all boxes checked:
```bash
drone @flow close FPLAN-0003
```
