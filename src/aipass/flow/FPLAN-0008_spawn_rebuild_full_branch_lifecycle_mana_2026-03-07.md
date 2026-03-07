# FPLAN-0008 - Spawn Rebuild — Full Branch Lifecycle Manager (MASTER PLAN)

**Created**: 2026-03-07
**Branch**: flow
**Status**: Active
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
1. The user provides planning doc or instructions (coordinate with @devpulse)
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
- **Status updates** - Quick progress lines so the user can glance without asking
- **Questions for the user** - Non-urgent questions that can wait for the next check-in
- **Notes to self** - Decisions made, things to revisit, gotchas discovered

Update it as you work - lightweight, not formal. The user checks it when they want to, skips it when busy. Low friction both ways.

```bash
# Create it at plan start
echo "# Notepad - FPLAN-0008" > notepad.md
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
drone @ai_mail send @devpulse "Subject" "Message"
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
Rebuild spawn from a create-only tool into a **full branch lifecycle manager** — matching and exceeding Dev-Pass cortex capabilities. When complete, spawn can create, update, delete, and sync branches. Template changes propagate system-wide with a single command. 100% seedgo audit compliance.

### Reference Documentation
- **Dev-Pass cortex** (reference, not source): `/home/coder/share/cortex/`
  - `apps/modules/update_branch.py` — 965-line update system (the crown jewel)
  - `apps/handlers/branch/change_detection.py` — ID-based rename detection
  - `apps/handlers/branch/reconcile.py` — pre/post-flight verification
  - `apps/handlers/json/ops.py` — deep merge + migrations
  - `apps/handlers/registry/meta_ops.py` — template registry + branch metadata ops
  - `apps/handlers/templates/sync.py` — managed file sync from source branches
- **Our spawn** (current state): `/home/coder/workspace/AIPass/src/aipass/spawn/`
- **Template**: `spawn/templates/agent.template/`
- **Existing tracking**: `.spawn/` dir per branch (template_registry, migrations stub, ignore files)
- **Registry**: `AIPASS_REGISTRY.json` at repo root

### Success Criteria
1. `drone @spawn create @newbranch` — creates branch from template (already works, wire through drone)
2. `drone @spawn update @branch` — fills missing scaffold, deep merges JSON, preserves code
3. `drone @spawn update --all` — batch update all branches
4. `drone @spawn sync-registry` — repair registry against filesystem
5. `drone @spawn delete @branch` — archive + deregister (with confirmation)
6. `.spawn/.branch_meta.json` tracks files by ID + hash per branch
7. `.spawn/.migrations.json` executes structural JSON transforms
8. Python files (.py) NEVER auto-overwritten — user code protected
9. Dry-run mode (`--dry-run`) for preview without execution
10. `drone @seedgo audit aipass` — spawn branch passes at highest possible score

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
- **Never delete** - devpulse manages cleanup
- Future: artifacts auto-roll to Memory Bank

---

## Phase Definitions

Define ALL phases before starting work:

### Phase 1: Drone Adapter + CLI Wiring
**Goal:** Make spawn routable via `drone @spawn` — currently spawn is only callable directly, not through drone routing.
**Agent Task:**
- Create `spawn/apps/handlers/drone_adapter.py` following the pattern from other branches (e.g., `drone/apps/handlers/module_registry.py`)
- Register spawn in drone's module registry so `drone @spawn` resolves
- Wire existing `create` command through adapter
- Add `--help` output listing all commands (create, update, delete, sync-registry)
- Stub command routing for future commands (update, delete, sync-registry) — they can return "not yet implemented"
**Deliverables:**
- `spawn/apps/handlers/drone_adapter.py`
- Updated module registry entry
- `drone @spawn --help` works
- `drone @spawn create` routes to existing create logic
- Tests in `spawn/tests/`

### Phase 2: Branch Metadata + Reconciliation Handlers
**Goal:** Build the tracking infrastructure that update depends on. Each branch needs `.spawn/.branch_meta.json` (ID-based file tracking with hashes). Need handlers for: loading/saving metadata, reconciling tracked state vs filesystem, and change detection.
**Agent Task:**
- Create `spawn/apps/handlers/meta_ops.py` — load/save `.branch_meta.json`, generate metadata for existing branches (scan filesystem, assign IDs, compute hashes)
- Create `spawn/apps/handlers/reconcile.py` — compare `.branch_meta.json` vs actual filesystem (missing files, untracked files, hash mismatches)
- Create `spawn/apps/handlers/change_detection.py` — compare template registry vs branch metadata: detect renames (by ID), additions, content updates (by hash), pruned files
- Create `spawn/apps/handlers/json_ops.py` — deep merge (template structure + existing values), load/apply migrations from `.migrations.json`
- Reference cortex handlers for logic patterns but use AIPass conventions (imports, prax logging, Path resolution)
**Deliverables:**
- `spawn/apps/handlers/meta_ops.py`
- `spawn/apps/handlers/reconcile.py`
- `spawn/apps/handlers/change_detection.py`
- `spawn/apps/handlers/json_ops.py`
- Tests in `spawn/tests/`

### Phase 3: Update Command
**Goal:** Build `drone @spawn update @branch` — the core feature. Uses Phase 2 handlers to: load tracking, detect changes, backup, apply changes (add missing files, deep merge JSON, archive pruned), update tracking.
**Agent Task:**
- Create `spawn/apps/modules/update.py` — orchestrator for the update workflow:
  1. Resolve branch path from registry
  2. Load `.spawn/.template_registry.json` + `.spawn/.branch_meta.json`
  3. If no branch_meta → generate from filesystem scan (first-time adoption)
  4. Pre-flight reconciliation (reconcile.py)
  5. Change detection (change_detection.py)
  6. If `--dry-run` → print what would change, exit
  7. Create backup of branch state
  8. Execute: renames → additions → JSON deep merges → archive pruned
  9. NEVER overwrite .py files — log as "manual review needed"
  10. Update `.spawn/.branch_meta.json` with new state
  11. Post-flight reconciliation to verify
- Wire `update` command into drone_adapter.py
- Support `--dry-run`, `--all` (batch), `--trace` (verbose logging)
**Deliverables:**
- `spawn/apps/modules/update.py`
- Updated `drone_adapter.py` with `update` routing
- `drone @spawn update @branch` works end-to-end
- `drone @spawn update --all` iterates all registered branches
- `drone @spawn update --dry-run @branch` previews without executing
- Tests in `spawn/tests/`

### Phase 4: Delete + Sync-Registry + Template Sync
**Goal:** Complete the lifecycle with delete (archive + deregister), registry repair, and managed file sync.
**Agent Task:**
- Create `spawn/apps/modules/delete.py`:
  - Move branch to `.archive/deleted_branches/{name}_{timestamp}/`
  - Remove from AIPASS_REGISTRY.json
  - Require `--yes` flag to skip confirmation (default: confirm)
  - Fire `branch_deleted` trigger event
- Create `spawn/apps/modules/sync_registry.py`:
  - Scan `src/aipass/` for branches with `.trinity/passport.json`
  - Compare against AIPASS_REGISTRY.json
  - Report stale entries (registered but missing) and unregistered branches
  - `--fix` flag to auto-repair
- Create `spawn/apps/modules/sync_templates.py`:
  - Define `template_owners.json` — maps template files to authoritative source branches
  - Pull latest versions of managed files from source branches into template
  - Example: if devpulse owns DASHBOARD.local.json schema → sync latest into template
- Wire all commands into drone_adapter.py
- Add `drone @spawn --help` showing complete command list
**Deliverables:**
- `spawn/apps/modules/delete.py`
- `spawn/apps/modules/sync_registry.py`
- `spawn/apps/modules/sync_templates.py`
- `spawn/apps/handlers/templates/template_owners.json`
- Updated `drone_adapter.py`
- Tests in `spawn/tests/`

### Phase 5: Seedgo Compliance + Integration Testing
**Goal:** Get spawn to highest possible seedgo audit score. End-to-end integration tests. Verify the full lifecycle: create → update → re-update after template change → delete.
**Agent Task:**
- Run `drone @seedgo audit aipass` and focus on spawn branch violations
- Fix all fixable violations (imports, structure, docstrings, logging)
- Create integration test suite:
  - Test create → verify scaffold complete
  - Test update on fresh branch → verify metadata generated
  - Test update after template change → verify additions detected
  - Test update --dry-run → verify no filesystem changes
  - Test JSON deep merge → verify values preserved, structure updated
  - Test .py file protection → verify Python never overwritten
  - Test delete → verify archive created + registry cleaned
  - Test sync-registry → verify stale/missing detection
- Update spawn README.md with complete API documentation
- Update spawn's `.trinity/` identity files
**Deliverables:**
- All seedgo violations fixed
- `spawn/tests/test_lifecycle.py` — integration test suite
- Updated `spawn/README.md`
- Updated `.trinity/passport.json` reflecting new capabilities
- Final `drone @seedgo audit aipass` report showing spawn score

---

## Execution Philosophy

### Autonomous Power-Through

Master plans are for **autonomous execution**. Don't halt production every phase waiting for review.

**The Pattern:**
- Power through all phases
- Accumulate issues as you go
- Deal with issues at the end
- The user reviews the final result, not every step

**Why this works:**
- Context is precious - don't burn it chasing bugs
- Complete picture reveals which issues actually matter
- Many "bugs" resolve themselves when later phases complete
- Coordination time is for decisions, not babysitting

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
- **Review happens at END** - not every phase

### Production Stop Protocol

If something causes production to STOP (critical blocker), **immediately email @devpulse**:

```bash
drone @ai_mail send @devpulse "PRODUCTION STOPPED: FPLAN-0008" "Phase X halted. Issue: [description]. Attempted: [what was tried]. Awaiting guidance."
```

**Never leave a branch stopped without reporting.** The orchestration hub needs visibility into all work.

### Monitoring Resources

For quick status checks and debugging, these resources are available:

| Resource | Location | Purpose |
|----------|----------|---------|
| Branch logs | `logs/` directory | Local execution logs |
| JSON tree | `apps/json_templates/` | Module firing status |
| Prax monitor | `drone @prax monitor` | Real-time system events |
| Seed audit | `drone @seed audit @branch` | Code quality check |

Use these when you need to confirm status or investigate issues.

### Agent Deployment Per Phase
Each phase = focused agent deployment:
1. Create sub-plan: `drone @flow create . "Phase X: [name]"`
2. Write agent instructions in sub-plan
3. Deploy agent with single-task focus
4. Review agent output (don't rebuild yourself)
5. Seed checklist on new code
6. Close sub-plan
7. Update memories
8. Email status to @devpulse
9. Next phase

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
- CROSS-BRANCH: Never modify other branches' files unless explicitly authorized by the user in the planning doc
- 2-ATTEMPT RULE: If something fails twice, note the issue and move on
- Do NOT go down rabbit holes debugging

WHEN COMPLETE:
- Verify code runs without syntax errors
- List files created/modified
- Note any issues encountered (with what was attempted)
```

---

## Phase Tracking

### Phase 1: Drone Adapter + CLI Wiring
- [ ] Sub-plan created: FPLAN-____
- [ ] Agent deployed
- [ ] Agent completed
- [ ] Output reviewed
- [ ] Seed checklist passed
- [ ] Sub-plan closed
- [ ] Memories updated
- [ ] Email sent to @devpulse
- **Status:** Pending
- **Notes:**

### Phase 2: Branch Metadata + Reconciliation Handlers
- [ ] Sub-plan created: FPLAN-____
- [ ] Agent deployed
- [ ] Agent completed
- [ ] Output reviewed
- [ ] Seed checklist passed
- [ ] Sub-plan closed
- [ ] Memories updated
- [ ] Email sent to @devpulse
- **Status:** Pending
- **Notes:**

### Phase 3: Update Command
- [ ] Sub-plan created: FPLAN-____
- [ ] Agent deployed
- [ ] Agent completed
- [ ] Output reviewed
- [ ] Seed checklist passed
- [ ] Sub-plan closed
- [ ] Memories updated
- [ ] Email sent to @devpulse
- **Status:** Pending
- **Notes:**

### Phase 4: Delete + Sync-Registry + Template Sync
- [ ] Sub-plan created: FPLAN-____
- [ ] Agent deployed
- [ ] Agent completed
- [ ] Output reviewed
- [ ] Seed checklist passed
- [ ] Sub-plan closed
- [ ] Memories updated
- [ ] Email sent to @devpulse
- **Status:** Pending
- **Notes:**

### Phase 5: Seedgo Compliance + Integration Testing
- [ ] Sub-plan created: FPLAN-____
- [ ] Agent deployed
- [ ] Agent completed
- [ ] Output reviewed
- [ ] Seed checklist passed
- [ ] Sub-plan closed
- [ ] Memories updated
- [ ] Email sent to @devpulse
- **Status:** Pending
- **Notes:**

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
- [ ] Full branch audit: `drone @seed audit @branch`
- [ ] Branch memories updated:
  - [ ] `BRANCH.local.json` - full session log
  - [ ] `BRANCH.observations.json` - patterns learned
- [ ] README.md updated (status, architecture, API - if build changed capabilities)
- [ ] Artifacts reviewed (devpulse manages cleanup)
- [ ] Final email to @devpulse:
  ```bash
  drone @ai_mail send @devpulse "FPLAN-0008 MASTER COMPLETE" "Full build summary: phases completed, deliverables, remaining issues (if any)"
  ```

**Completion Order:** Memories → README → Email (README before email - don't report complete with stale docs)

**Note:** Devpulse will perform its own Seed audit for visibility into the work.

### Definition of Done
1. All 5 commands work via drone: `create`, `update`, `delete`, `sync-registry`, `sync-templates`
2. `drone @spawn update --all` successfully updates all 10 branches from template
3. `.spawn/.branch_meta.json` exists in every branch with ID-based tracking
4. JSON deep merge preserves existing values while adopting template structure changes
5. Python files are never auto-overwritten during updates
6. `--dry-run` mode works for update and delete
7. Integration tests pass for full lifecycle (create → update → delete)
8. `drone @seedgo audit aipass` — spawn scores highest possible
9. spawn README.md documents complete API
10. spawn `.trinity/` identity reflects lifecycle manager role

---

## Close Command

When ALL phases complete and checklist done:
```bash
drone @flow close FPLAN-0008
```
