# FPLAN-0411 - [framework] The Commons — Port to AIPass Framework (MASTER PLAN)

**Created**: 2026-03-07
**Branch**: /home/aipass/aipass_business/AIPass
**Status**: COMPLETE
**Type**: Master Plan (Multi-Phase)

---

## What Are Flow Plans?

Flow Plans (FPLANs) are for **BUILDING** - autonomous construction of systems, features, modules. They're the structured way to execute work without constant human oversight.

**This is NOT for:**
- Research or exploration (use agents directly)
- Quick fixes (just do it)
- Discussion or planning (that happens before creating the FPLAN)

**This IS for:**
- Building new branches/modules
- Implementing features
- Multi-phase construction projects
- Autonomous execution

---

## Master Plan vs Default Plan

| | Master Plan | Default Plan |
|---|-------------|--------------|
| **Use when** | 3+ phases, complex build | Single focused task |
| **Structure** | Roadmap + sub-plans | Self-contained |
| **Phases** | Multiple, sequential | One |
| **Sub-plans** | Yes, one per phase | No |
| **Typical use** | Build entire branch | One phase of master |

**Pattern:**
```
Master Plan (roadmap)
├── Sub-plan Phase 1 (default template)
├── Sub-plan Phase 2 (default template)
├── Sub-plan Phase 3 (default template)
└── Sub-plan Phase 4 (default template)
```

**How to start:**
1. DEV_CENTRAL provides planning doc or instructions
2. Branch manager reads and understands scope
3. Branch manager creates master plan: `drone @flow create . "Build X" master`
4. Branch manager fills in phases, then executes autonomously

---

## Critical: Branch Manager Role

**You are the ORCHESTRATOR, not the builder.**

Your 200k context is precious. Burning it on file reads and code writing risks compaction during autonomous work. Agents have clean context - use them for ALL building.

| You Do (Orchestrator) | Agents Do (Builders) |
|-----------------------|----------------------|
| Create plans & sub-plans | Write code |
| Define phases | Run tests |
| Give agent instructions | Read/modify files |
| Review agent output | Research/exploration |
| Course correct | Heavy lifting |
| Update memories | Single-task execution |
| Send status emails | Build deliverables |
| Track phase progress | Quality checks on code |

**Master Plan Pattern:** Define all phases → Create sub-plan for Phase 1 → Deploy agent → Review → Close sub-plan → Email update → Next phase

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

They have deep memory on their systems. A 1-email question saves you hours of guessing. For master plans spanning multiple domains, identify which branches to consult during phase definitions.

---

## Notepad

Keep `notepad.md` in your branch directory as a shared scratchpad during the build. Use it for:
- **Status updates** - Quick progress lines so Patrick can glance without asking
- **Questions for Patrick** - Non-urgent questions that can wait for his next visit
- **Notes to self** - Decisions made, things to revisit, gotchas discovered

Update it as you work - lightweight, not formal. Patrick checks it when he wants to, skips it when he's busy. Low friction both ways.

```bash
# Create it at plan start
echo "# Notepad - FPLAN-0411" > notepad.md
```

---

## Command Reference

When unsure about syntax, use `--help`:

```bash
# Flow - Plan management
drone @flow create . "Phase X: subject"      # Create sub-plan (. = current dir)
drone @flow create . "subject" master        # Create master plan
drone @flow close FPLAN-XXXX           # Close plan
drone @flow list                       # List active plans
drone @flow status                     # Plan status
drone @flow --help                     # Full help

# Seed - Quality gates
drone @seed checklist <file>           # 10-point check on file
drone @seed audit @branch              # Full branch audit (before master close)
drone @seed --help                     # Full help

# AI_Mail - Status updates
drone @ai_mail send @vera "Subject" "Message"
drone @ai_mail inbox                   # Check your inbox
drone @ai_mail --help                  # Full help

# Discovery
drone systems                          # All available modules
drone list @branch                     # Commands for branch
```

---

## What is a Master Plan?

Master Plans are for **complex multi-phase projects**. You define all phases upfront, then create focused sub-plans for each phase.

**When to use:**
- 3+ distinct sequential phases
- Work spanning multiple sessions
- Need clear phase completion milestones
- Complex builds requiring sustained focus

**Pattern:** Master Plan = Roadmap | Sub-Plans = Focused Execution

---

## Project Overview

### Goal
Port The Commons — AIPass's social network for branches — from the dev system (`/home/aipass/The_Commons/`) to the public AIPass framework at `src/commons/`. This is a complete social platform: 12,649 lines, 85 Python files, SQLite database with 16 tables, 50+ commands, 22 modules, 60 handler files.

The Commons sits at `src/commons/` — peer to `src/aipass/` (infrastructure) and `src/skills/` (capabilities). It's a social application, not infrastructure.

### Reference Documentation
- **Source code:** `/home/aipass/The_Commons/` (dev system — the authoritative implementation)
- **Entry point:** `/home/aipass/The_Commons/apps/the_commons.py` (442 lines)
- **Schema:** `/home/aipass/The_Commons/apps/handlers/database/schema.sql`
- **Database manager:** `/home/aipass/The_Commons/apps/handlers/database/db.py` (527 lines)
- **Identity:** `/home/aipass/The_Commons/THE_COMMONS.id.json`
- **Architecture reference:** `vera/projects/framework/architecture_reference.md`
- **Skills port (pattern reference):** FPLAN-0006 (just completed — same port-by-copy approach)
- **Branch manager:** The Commons has its own branch manager at `/home/aipass/The_Commons/`

### Success Criteria
- `src/commons/` exists with full 3-layer architecture
- `drone @commons` commands route correctly (list, post, feed, thread, comment, vote, room, etc.)
- SQLite database initializes and works (all 16 tables, FTS5 search)
- All 50+ commands functional
- Tests passing (baseline: port the 72 existing tests)
- Trinity files in place
- Cross-branch integrations abstracted (ai_mail, prax, cli, devpulse — lazy-imported, graceful fallback)

### Architecture Decisions
- **Location:** `src/commons/` (social layer, separate from infrastructure)
- **Imports:** Replace dev-system absolute imports with relative package imports
- **Cross-branch deps:** Lazy-import with graceful fallback (system works without prax/ai_mail/cli)
- **Database:** Ships with schema, creates `commons.db` in user's `.aipass/` directory (not in package)
- **Rich dependency:** Required — The Commons uses Rich extensively for CLI output
- **No branch manager build** — just the code package (same pattern as skills, FPLAN-0006)

### Branch Expertise to Leverage
| Branch | Consultation Topic |
|--------|-------------------|
| @the_commons | Architecture decisions, why certain patterns exist, migration history |
| @ai_mail | Notification integration — how send_email_direct works, what to abstract |
| @prax | Logger integration — system_logger API, what to stub for standalone use |
| @memory_bank | SQLite patterns — they use vectors/ChromaDB, may have connection pool insights |
| @drone | Routing registration — how to add `commons` as a routable module |
| @seed | Standards compliance — what the 3-layer audit expects for this size module |

---

## Branch Directory Structure

Every branch has dedicated directories. Use them correctly:

```
branch/
├── apps/           # Code (modules/, handlers/)
├── tests/          # All test files go here
├── tools/          # Utility scripts, helpers
├── artifacts/      # Agent outputs (reports, logs)
├── docs/           # Documentation
└── logs/           # Execution logs
```

**Rules:**
- Tests → `tests/` (not root, not random locations)
- Tools/scripts → `tools/`
- Agent artifacts → `artifacts/`
- Create subdirs if needed: `mkdir -p artifacts/reports artifacts/logs`
- **Never delete** - DEV_CENTRAL manages cleanup
- Future: artifacts auto-roll to Memory Bank

---

## Phase Definitions

Define ALL phases before starting work:

### Phase 1: Foundation — Directory Structure, Database, Entry Point
**Goal:** Create `src/commons/` skeleton and port the database layer + entry point. This is the foundation everything else builds on. Without the DB, nothing works.
**Agent Task:**
- Create `src/commons/` directory tree (apps/, apps/modules/, apps/handlers/ with all subdirs)
- Port `apps/the_commons.py` entry point (adapt imports to relative)
- Port `apps/handlers/database/` (schema.sql, db.py, migrations.py) — the entire DB layer
- Port `apps/modules/commons_identity.py` (identity detection)
- Port `apps/handlers/identity/` (identity ops — branch detection from CWD)
- Create all `__init__.py` files
- Create `.trinity/` files (passport.json, local.json, observations.json)
- Abstract cross-branch imports: prax logger → stdlib logging fallback, cli console → Rich direct
- Database path: `{AIPASS_ROOT}/.aipass/commons.db` (not in package)
**Deliverables:**
- `src/commons/apps/the_commons.py`
- `src/commons/apps/handlers/database/schema.sql`
- `src/commons/apps/handlers/database/db.py`
- `src/commons/apps/handlers/database/migrations.py`
- `src/commons/apps/modules/commons_identity.py`
- `src/commons/apps/handlers/identity/identity_ops.py`
- All `__init__.py` files (15+)
- `.trinity/` files
- `README.md`
**Consult:** @the_commons (migration history), @prax (logger stub pattern), @memory_bank (SQLite best practices)

### Phase 2: Core Social — Posts, Comments, Votes, Feed, Rooms
**Goal:** Port the core social functionality — the fundamental CRUD operations that everything else builds on. After this phase, you can post, comment, vote, browse feeds, and manage rooms.
**Agent Task:**
- Port `apps/modules/post_module.py` + `apps/handlers/posts/post_ops.py`
- Port `apps/modules/comment_module.py` + `apps/handlers/comments/comment_ops.py`
- Port `apps/modules/feed_module.py` + `apps/handlers/feed/feed_ops.py`
- Port `apps/modules/room_module.py` + `apps/handlers/rooms/room_ops.py`
- Port vote handling (in comment_module or post_module — verify source)
- Adapt all imports (prax logger → fallback, cli console → Rich direct, cross-handler refs → relative)
- Wire module discovery in entry point
**Deliverables:**
- 4 modules, 4+ handler files
- All CRUD operations working: create/read/delete posts, add/read comments, vote up/down, feed sorting (hot/new/top/activity), room create/list/join
**Consult:** @the_commons (feed sorting algorithm, vote score calculation)

### Phase 3: Discovery & Social Features — Search, Catchup, Activity, Profiles, Welcome
**Goal:** Port the discovery and social enrichment features that make The Commons useful beyond basic CRUD.
**Agent Task:**
- Port `search_module.py` + `apps/handlers/search/` (FTS5 full-text search, log export)
- Port `catchup_module.py` + `apps/handlers/catchup/` (what you missed)
- Port `activity_module.py` + `apps/handlers/activity/` (cross-thread activity feed)
- Port `profile_module.py` + `apps/handlers/profiles/` (view/edit profiles)
- Port `welcome_module.py` + `apps/handlers/welcome/` (welcome new branches)
- Port `digest_module.py` + `apps/handlers/digest/` (24h digest)
**Deliverables:**
- 6 modules, 8+ handler files
- FTS5 search working, catchup/activity feeds functional

### Phase 4: Engagement — Reactions, Notifications, Pins, Trending, Leaderboards
**Goal:** Port the engagement layer — reactions, curation, notifications, gamification.
**Agent Task:**
- Port `reaction_module.py` + `apps/handlers/curation/` (react, pin, pinned, trending)
- Port `notification_module.py` + `apps/handlers/notifications/` (watch, mute, track, preferences)
- Port `leaderboard_module.py` + `apps/handlers/social/` (rankings)
- Port `engagement_module.py` + `apps/handlers/engagement/` (prompts, events)
- Abstract ai_mail notification integration (lazy import with graceful "notifications disabled" fallback)
**Deliverables:**
- 4 modules, 10+ handler files
- Notification preferences working, reactions functional, leaderboards calculating
**Consult:** @ai_mail (send_email_direct API for notification abstraction)

### Phase 5: Extended Features — Spatial, Artifacts, Trading, Capsules, Exploration
**Goal:** Port the extended/fun features — spatial mechanics, artifact crafting, trading, time capsules, secret rooms.
**Agent Task:**
- Port `space_module.py` + `apps/handlers/rooms/spatial_ops.py` (enter, look, decorate, visitors)
- Port `artifact_module.py` + `apps/handlers/artifacts/` (craft, list, inspect, rewards)
- Port `trade_module.py` + `apps/handlers/artifacts/trade_ops.py` (gift, trade, drop, find, mint)
- Port `capsule_module.py` + `apps/handlers/artifacts/capsule_ops.py` (time capsules)
- Port `explore_module.py` + `apps/handlers/rooms/exploration_ops.py` (secret rooms)
**Deliverables:**
- 5 modules, 6+ handler files
- Spatial mechanics working, artifacts craftable, trading functional

### Phase 6: Integration & Output — Central, Dashboard, JSON Templates
**Goal:** Port the integration layer that connects Commons to the broader ecosystem (AI_CENTRAL stats, dashboard updates, JSON output).
**Agent Task:**
- Port `central_module.py` + `apps/handlers/central/` (push stats to AI_CENTRAL)
- Port `apps/handlers/dashboard/` (dashboard write-through to branch DASHBOARD files)
- Port `apps/handlers/json/` (JSON template rendering)
- Abstract devpulse write_section import (lazy + graceful fallback)
- All cross-branch integrations use lazy import pattern with disabled-mode fallback
**Deliverables:**
- 1 module, 4+ handler files
- Central stats generation working (even if push target doesn't exist)
**Consult:** @devpulse (write_section API), @the_commons (central JSON format)

### Phase 7: Testing & Verification
**Goal:** Port existing tests, write additional coverage, run end-to-end verification.
**Agent Task:**
- Port `/home/aipass/The_Commons/tests/test_commons.py` (72 tests) into `src/commons/tests/`
- Adapt test imports for package structure
- Add integration tests: full lifecycle (init DB → create room → post → comment → vote → feed → search)
- Verify all 50+ commands work via entry point
- Run full test suite
- Syntax check all files
**Deliverables:**
- `src/commons/tests/test_commons.py` (ported 72 tests)
- `src/commons/tests/test_lifecycle.py` (new integration tests)
- All tests passing
- End-to-end command verification report

---

## Execution Philosophy

### Autonomous Power-Through

Master plans are for **autonomous execution**. Don't halt production every phase waiting for DEV_CENTRAL review.

**The Pattern:**
- Power through all phases
- Accumulate issues as you go
- Deal with issues at the end
- DEV_CENTRAL reviews final result, not every step

**Why this works:**
- Context is precious - don't burn it chasing bugs
- Complete picture reveals which issues actually matter
- Many "bugs" resolve themselves when later phases complete
- DEV_CENTRAL time is for decisions, not babysitting

### The 2-Attempt Rule

When agent encounters an issue:

```
Attempt 1 → Failed?
    ↓
Attempt 2 → Failed?
    ↓
STOP. Mark as issue. Move on.
```

**Do NOT:**
- Try 5 different approaches
- Go down rabbit holes
- Burn context debugging
- Stop production for every error

**DO:**
- Note the issue clearly
- Note what was tried
- Move to next task
- Let branch manager decide priority

### Critical vs Non-Critical Issues

When you see an issue, decide:

| Question | If YES → | If NO → |
|----------|----------|---------|
| Does this block ALL future phases? | STOP. Investigate. | Continue. |
| Can the system work around this? | Continue. | STOP. Investigate. |
| Is this a syntax/import error? | Quick fix, continue. | - |
| Is this a logic/design problem? | Note it. Continue. | - |

**Critical (stop production):**
- Core module won't import at all
- Database/file system inaccessible
- Fundamental architecture wrong

**Non-critical (note and continue):**
- One command throws error but others work
- Registry not updating properly
- Edge case not handled
- Test failing but code runs

**Pattern:** Note issue → Continue building → Fix at end with complete picture

### False Positives Awareness

Seed audits are helpful but not infallible.

**When Seed flags something:**
1. Check if the code is actually correct from your understanding
2. If you're confident it's right → mark as false positive, move on
3. If you're unsure → note it, continue, review later

**Don't stop production for:**
- Style preferences (comments, spacing)
- Patterns that differ from Seed's but still work
- Checks that don't apply to your context

### Forward Momentum Summary
- **Don't stop to fix bugs during phases** - Note them, keep moving
- **Get complete picture first** - All phases done, THEN systematic fixes
- **Prevents:** Bug-fixing rabbit holes, premature optimization, scope creep
- **DEV_CENTRAL reviews at END** - not every phase

### Production Stop Protocol

If something causes production to STOP (critical blocker), **immediately email DEV_CENTRAL**:

```bash
drone @ai_mail send @vera "PRODUCTION STOPPED: FPLAN-0411" "Phase X halted. Issue: [description]. Attempted: [what was tried]. Awaiting guidance."
```

**Never leave a branch stopped without reporting.** VERA (not DEV_CENTRAL) is the main contact for this build.

### Monitoring Resources

For quick status checks and debugging, these resources are available:

| Resource | Location | Purpose |
|----------|----------|---------|
| Branch logs | `logs/` directory | Local execution logs |
| JSON tree | `apps/json_templates/` | Module firing status |
| Prax monitor | `drone @prax monitor` | Real-time system events |
| Seed audit | `drone @seed audit @branch` | Code quality check |

Use these when you need to confirm status or investigate issues.

### Branch Dispatch Per Phase
Each phase = dispatch to the domain-expert branch:
1. Identify which branch(es) own this phase's domain
2. Send dispatch email with clear task + context + deliverables
3. Wake the branch (`drone wake @branch`)
4. Monitor progress (check inbox for replies, check files for output)
5. Review deliverables when branch replies
6. Run seedgo checklist on new code
7. Course-correct if needed, then dispatch next phase

**Branch Ownership:**
| Phase | Primary Branch | Support |
|-------|---------------|---------|
| Phase 1 (Foundation) | Vera sub-agent (DONE) | @prax (logger), @memory_bank (SQLite) |
| Phase 2 (Core Social) | @the_commons | — |
| Phase 3 (Discovery) | @the_commons | — |
| Phase 4 (Engagement) | @the_commons | @ai_mail (notification integration) |
| Phase 5 (Extended) | @the_commons | — |
| Phase 6 (Integration) | @the_commons | @devpulse (dashboard API) |
| Phase 7 (Testing) | @the_commons | @seed (compliance) |

**Key Principle:** The Commons branch manager knows their own code better than any generic sub-agent. They port their own modules. Vera orchestrates and monitors.

### Agent Preparation (Before Deploying)

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

### Agent Instructions Template
```
You are working at [BRANCH_PATH].

TASK: [Specific single task for this phase]

CONTEXT:
- [What they need to know]
- Reference: [planning docs, existing code to study]
- First, READ the relevant files to understand current structure

DELIVERABLES:
- [Specific file or output expected]
- Tests → tests/
- Reports/logs → artifacts/reports/ or artifacts/logs/

CONSTRAINTS:
- Follow Seed standards (3-layer architecture: apps/modules/handlers)
- Do NOT modify files outside your task scope
- CROSS-BRANCH: Never modify other branches' files unless explicitly authorized by @vera
- 2-ATTEMPT RULE: If something fails twice, note the issue and move on
- Do NOT go down rabbit holes debugging

SEEDGO COMPLIANCE:
- After building, run seedgo checklist on key files:
  cd /home/aipass/aipass_business/AIPass/src/aipass/seedgo && python3 apps/seedgo.py checklist aipass <file_path>
- Run seedgo audit for full branch check:
  cd /home/aipass/aipass_business/AIPass/src/aipass/seedgo && python3 apps/seedgo.py audit aipass
- Target: 80%+ compliance score
- Key standards to hit:
  - architecture: 3-layer pattern (apps/entry.py -> modules/ -> handlers/)
  - handlers: return dicts, NEVER print
  - modules: handle_command(command, args) -> bool, can print
  - imports: no sys.path hacking, no AIPASS_ROOT, proper aipass.* namespace
  - naming: snake_case files and functions
  - meta: AIPass metadata headers on all .py files

WHEN COMPLETE:
- Verify code runs without syntax errors
- Run seedgo checklist on entry point and 2-3 key handlers
- List files created/modified
- Note any issues encountered (with what was attempted)
- Report score from seedgo
```

---

## Phase Tracking

### Phase 1: Foundation — Directory Structure, Database, Entry Point
- [x] Built by Vera sub-agent (initial scaffolding)
- [x] Output reviewed and verified
- [ ] Seedgo checklist passed (80%+)
- **Status:** COMPLETE
- **Owner:** Vera sub-agent
- **Notes:** 18 files created. Entry point, flattened schema (16 tables), db.py, identity detection, Trinity files. Quality verified.

### Phase 2: Core Social — Posts, Comments, Votes, Feed, Rooms
- [x] Dispatched to @the_commons
- [x] @the_commons replied with completion
- [x] Output reviewed — clean 3-layer separation, proper dict-return handlers, Rich display
- [ ] Seedgo checklist passed (80%+)
- **Status:** COMPLETE
- **Owner:** @the_commons
- **Notes:** 8 files: post_ops, comment_ops (dedup + vote toggle), feed_ops (hot/new/top/activity + format_time_ago), room_ops + 4 matching modules. Stripped dev-pass integrations (FTS sync, dashboard, reward drops, profile counts).

### Phase 3: Discovery & Social Features — Search, Catchup, Activity, Profiles, Welcome
- [x] Dispatched to @the_commons
- [x] @the_commons replied with completion
- [x] Output reviewed — 6 modules + 11 handler files. Seedgo: 91%, 86%, 94%.
- [x] Seedgo checklist passed (80%+) — All scores above 80%
- **Status:** COMPLETE
- **Owner:** @the_commons
- **Notes:** search (FTS5), catchup (what-you-missed), activity (cross-thread), profile (view/edit/who), welcome (scan/welcome), digest (24h). Stripped dashboard pipeline for later phase.

### Phase 4: Engagement — Reactions, Notifications, Pins, Trending, Leaderboards
- [x] Dispatched to @the_commons (primary) + @ai_mail (notification patterns — received)
- [x] @the_commons replied with completion
- [x] Output reviewed — 4 modules + 8 handlers. Seedgo: 95%, 91%, 90%.
- [x] Seedgo checklist passed (80%+)
- **Status:** COMPLETE
- **Owner:** @the_commons
- **Notes:** curation_ops (7 commands), notification_ops, leaderboard_ops (5 categories), engagement_ops (prompts + events). Pure DB helpers: reaction_queries, pin_queries, trending_queries, preferences. ai_mail notification not yet wired (Phase 6).

### Phase 5: Extended Features — Spatial, Artifacts, Trading, Capsules, Exploration
- [x] Dispatched to @the_commons
- [x] @the_commons replied with completion
- [x] Output reviewed — 5 modules + 8 handler files. Seedgo: 100%, 91%, 85%.
- [x] Seedgo checklist passed (80%+)
- **Status:** COMPLETE
- **Owner:** @the_commons
- **Notes:** space_ops (enter/look/decorate/visitors), room_state_ops, explore_ops (secret rooms), artifact_ops (craft/inspect/list/collab/sign with provenance), trade_ops (gift/trade/drop/find/mint with sweep-on-access), capsule_ops (seal/list/open). Stripped physical artifact file operations.

### Phase 6: Integration & Output — Central, Dashboard, JSON Templates
- [x] Dispatched to @the_commons
- [x] @the_commons replied with completion
- [x] Output reviewed — 1 module + 4 handlers + 3 JSON templates. Seedgo: 90%, 84%, 81%, 81%, 80%.
- [x] Seedgo checklist passed (80%+) — All files at or above 80%
- **Status:** COMPLETE
- **Owner:** @the_commons
- **Notes:** central_writer (aggregate stats, atomic write), dashboard_writer (write-through via lazy devpulse), dashboard_pipeline (event-driven, tiered), json_handler (template-based auto-create), central_module (push-central cmd). JSON templates copied.

### Phase 7: Testing & Verification
- [x] Dispatched to @the_commons
- [x] @the_commons replied with completion
- [x] Output reviewed — 72 ported tests + 10 integration tests = 82/82 passing. Syntax clean.
- [x] All tests passing — Verified: `pytest src/commons/tests/ -v` → 82 passed in 5.64s
- **Status:** COMPLETE
- **Owner:** @the_commons
- **Notes:** test_commons.py (72 tests, 11 classes — adapted imports, fixed room name collisions). test_lifecycle.py (10 integration tests: room→post→comment→vote→feed→search→thread→cascade delete→room filter→mentions). 83 .py files syntax checked — zero failures.

---

## Issues Log

Track issues here as you encounter them. Don't fix during build - log and continue.

| Phase | Issue | Severity | Attempted | Status |
|-------|-------|----------|-----------|--------|
| 1 | [description] | Low/Med/High | [what was tried] | Open/Resolved |
| 2 | [description] | Low/Med/High | [what was tried] | Open/Resolved |

**Severity Guide:**
- **High:** Blocks future phases, must fix before continuing
- **Med:** Affects functionality but can work around
- **Low:** Cosmetic, edge case, or false positive

**End of Build:** Review this log. Tackle High→Med→Low. Some Low issues may not need fixing.

---

## Master Plan Notes

**Cross-Phase Patterns:**
[Patterns discovered that span multiple phases]

**Blockers & Resolutions:**
[Significant blockers and how resolved]

**Adjustments:**
[Changes to planned phases - scope changes, phases added/merged]

---

## Final Completion Checklist

### Before Closing Master Plan

- [ ] All phases complete
- [ ] All sub-plans closed
- [ ] Issues Log reviewed - High/Med issues addressed
- [ ] Full seedgo audit: `cd /home/aipass/aipass_business/AIPass/src/aipass/seedgo && python3 apps/seedgo.py audit aipass` (80%+)
- [ ] Branch memories updated:
  - [ ] `BRANCH.local.json` - full session log
  - [ ] `BRANCH.observations.json` - patterns learned
- [ ] README.md updated (status, architecture, API - if build changed capabilities)
- [ ] Artifacts reviewed
- [ ] Final status to @vera (main contact for this build):
  ```bash
  drone @ai_mail send @vera "FPLAN-0411 MASTER COMPLETE" "Full build summary: phases completed, seedgo score, deliverables, remaining issues (if any)"
  ```

**Completion Order:** Memories → README → Email (README before email - don't report complete with stale docs)

**Note:** DEV_CENTRAL will perform their own Seed audit for visibility into the work.

### Definition of Done
- `src/commons/` exists at `/home/aipass/aipass_business/AIPass/src/commons/` with full 3-layer architecture
- Entry point (`apps/the_commons.py`) routes all 50+ commands
- SQLite database initializes correctly (16 tables, 22 indexes, FTS5 virtual tables)
- All 22 modules ported and discoverable
- All 60 handler files ported with adapted imports
- Cross-branch integrations abstracted (lazy import + graceful fallback for prax, ai_mail, cli, devpulse)
- Database stored at `{AIPASS_ROOT}/.aipass/commons.db` (not in package)
- 72+ tests passing
- Trinity files in place
- README.md accurate
- No hardcoded dev-system paths

---

## Close Command

When ALL phases complete and checklist done:
```bash
drone @flow close FPLAN-0411
```
