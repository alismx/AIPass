# FPLAN-0009 - Citizen Classes — Template System + Passport Command (MASTER PLAN)

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
- Unsure about standards? Ask @seedgo for reference code
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
echo "# Notepad - FPLAN-0009" > notepad.md
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

# Seedgo - Quality gates
drone @seedgo checklist <file>           # 10-point check on file
drone @seedgo audit @branch              # Full branch audit (before master close)
drone @seedgo --help                     # Full help

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
Evolve spawn from a single-template system into a **class-based template system** where citizens have different types (builder, manager, researcher, birthright). Each class has its own template. Commands become class-aware. `update --all` scopes by class. A new `passport` command grants lightweight citizenship without full scaffold.

### Reference Documentation
- **Current spawn**: `/home/coder/workspace/AIPass/src/aipass/spawn/`
- **Current template**: `spawn/templates/agent.template/` (becomes `builder` template)
- **FPLAN-0008**: Spawn rebuild plan (completed — lifecycle commands working)
- **Session 7 design discussion**: citizen_classes key in local.json + MEMORY.md
- **Dev-Pass cortex templates**: `/home/coder/share/cortex/templates/` (had branch, business_branch, team — same concept, different naming)
- **daemon branch**: `/home/coder/workspace/AIPass/src/aipass/daemon/` — the real-world case that drove this design (needs citizenship without apps/)

### Success Criteria
1. `drone @spawn create builder @newbranch` — creates full 3-layer branch (current behavior, new syntax)
2. `drone @spawn create manager @ops` — creates manager-class citizen (lighter template)
3. `drone @spawn passport @daemon` — grants birthright only (.trinity/ + .aipass/ + registry)
4. `drone @spawn update builder --all` — updates only builder-class branches
5. `drone @spawn update --all` — BLOCKED with "specify a class" message
6. Passport stores `citizen_class` field — spawn reads it for routing
7. `agent.template/` renamed to `builder/` in templates dir
8. At least 2 templates: `builder` (full) and `birthright` (minimal)
9. All existing branches get `citizen_class: "builder"` in passport
10. 84+ tests still passing, new tests for class-based features

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

### Phase 1: Template Restructure + Class Registry
**Goal:** Reorganize templates directory from single template to class-based structure. Create a class registry that maps class names to template dirs. Rename `agent.template/` to `builder/`.
**Agent Task:**
- Rename `spawn/templates/agent.template/` to `spawn/templates/builder/`
- Create `spawn/templates/birthright/` with minimal template:
  - `.trinity/passport.json` (with `citizen_class: "birthright"`)
  - `.trinity/local.json` (empty session template)
  - `.trinity/observations.json` (empty observations template)
  - `.aipass/branch_system_prompt.md` (placeholder prompt)
  - `README.md` (minimal)
  - `.spawn/.template_registry.json` (generated)
- Create `spawn/apps/handlers/class_registry.py`:
  - `CITIZEN_CLASSES` dict mapping class name → template dir
  - `get_template_dir(citizen_class)` → returns Path to template
  - `get_available_classes()` → returns list of class names
  - `validate_class(name)` → bool
- Update `spawn/apps/handlers/meta_ops.py` → `get_template_dir()` now accepts optional `citizen_class` param (default: "builder")
- Update all references to `agent.template` across spawn code
- Update `spawn/templates/agent_mock_branch/` references if needed
- Generate `.template_registry.json` for both builder and birthright templates
**Deliverables:**
- `spawn/templates/builder/` (renamed from agent.template)
- `spawn/templates/birthright/` (new minimal template)
- `spawn/apps/handlers/class_registry.py`
- Updated meta_ops.py
- All existing tests still pass

### Phase 2: Passport Command + Class-Aware Create
**Goal:** Build the `passport` command for lightweight citizenship. Make `create` class-aware with new syntax.
**Agent Task:**
- Create `spawn/apps/modules/passport.py` (thin module) + `spawn/apps/handlers/passport_ops.py` (implementation):
  - `drone @spawn passport @dirname` — grants birthright to existing directory
  - Creates .trinity/ with passport (citizen_class: "birthright"), local.json, observations.json
  - Creates .aipass/ with branch_system_prompt.md
  - Registers in AIPASS_REGISTRY.json
  - Accepts `--role`, `--purpose` flags for passport fields
  - If directory doesn't exist, creates it
  - If .trinity/ already exists, error: "already a citizen"
- Update `spawn/apps/spawn.py` to route `passport` command
- Update `create` command to accept class as first arg:
  - `drone @spawn create builder @path` (explicit class)
  - `drone @spawn create @path` (default: builder, backward compatible)
- Wire class through to `_spawn_agent()` in core.py → passes class to template selection
- Add `citizen_class` field to passport.json template and create logic
**Deliverables:**
- `spawn/apps/modules/passport.py`
- `spawn/apps/handlers/passport_ops.py`
- Updated `spawn/apps/spawn.py` with passport + class-aware create
- Updated `spawn/apps/modules/core.py` with class routing
- Tests for passport command

### Phase 3: Class-Aware Update + Profile Check
**Goal:** Make update class-aware. `update --all` requires class. Update checks passport's citizen_class to know which template applies. Light citizens don't get builder scaffold forced on them.
**Agent Task:**
- Update `spawn/apps/handlers/update_ops.py`:
  - `update_branch()` reads passport.json → gets `citizen_class` → selects correct template
  - If no citizen_class in passport → default to "builder" (backward compat for existing branches)
  - Template comparison uses class-appropriate template dir
- Update `update_all()`:
  - REQUIRE class arg: `update_all(citizen_class, dry_run, trace)`
  - `drone @spawn update --all` without class → error message: "Specify a class: drone @spawn update builder --all"
  - `drone @spawn update builder --all` → only updates branches with citizen_class="builder"
  - `drone @spawn update birthright --all` → only updates birthright branches
- Update CLI parsing in `spawn/apps/modules/update.py`:
  - `["builder", "--all"]` → update all builders
  - `["builder", "@branch"]` → update specific branch as builder
  - `["@branch"]` → update using branch's own citizen_class from passport
  - `["--all"]` → blocked
- Backfill: add `citizen_class: "builder"` to all 10 existing branch passports
**Deliverables:**
- Updated `spawn/apps/handlers/update_ops.py`
- Updated `spawn/apps/modules/update.py`
- All 10 existing passports updated with citizen_class
- Tests for class-scoped update

### Phase 4: Integration Testing + Seedgo Compliance
**Goal:** End-to-end testing of the full class system. Verify seedgo compliance.
**Agent Task:**
- Create integration tests:
  - `passport @dirname` → verify birthright files created, registered
  - `create builder @path` → verify full scaffold
  - `create @path` → verify backward compat (defaults to builder)
  - `update builder --all` → only touches builders, skips birthright
  - `update --all` → blocked with clear error
  - `update @birthright_branch` → uses birthright template, doesn't add apps/
  - `passport` on existing citizen → error
  - `delete @birthright_branch` → archive works for light citizens too
- Run `drone @seedgo audit aipass` → fix any new violations
- Update spawn README.md with new command syntax
- Update spawn --help text
**Deliverables:**
- `spawn/tests/test_citizen_classes.py`
- Updated README.md
- Seedgo compliance maintained
- All tests passing

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

Seedgo audits are helpful but not infallible.

**When Seedgo flags something:**
1. Check if the code is actually correct from your understanding
2. If you're confident it's right → mark as false positive, move on
3. If you're unsure → note it, continue, review later

**Don't stop production for:**
- Style preferences (comments, spacing)
- Patterns that differ from Seedgo's but still work
- Checks that don't apply to your context

### Forward Momentum Summary
- **Don't stop to fix bugs during phases** - Note them, keep moving
- **Get complete picture first** - All phases done, THEN systematic fixes
- **Prevents:** Bug-fixing rabbit holes, premature optimization, scope creep
- **Review happens at END** - not every phase

### Production Stop Protocol

If something causes production to STOP (critical blocker), **immediately email @devpulse**:

```bash
drone @ai_mail send @devpulse "PRODUCTION STOPPED: FPLAN-0009" "Phase X halted. Issue: [description]. Attempted: [what was tried]. Awaiting guidance."
```

**Never leave a branch stopped without reporting.** The orchestration hub needs visibility into all work.

### Monitoring Resources

For quick status checks and debugging, these resources are available:

| Resource | Location | Purpose |
|----------|----------|---------|
| Branch logs | `logs/` directory | Local execution logs |
| JSON tree | `apps/json_templates/` | Module firing status |
| Prax monitor | `drone @prax monitor` | Real-time system events |
| Seedgo audit | `drone @seedgo audit @branch` | Code quality check |

Use these when you need to confirm status or investigate issues.

### Agent Deployment Per Phase
Each phase = focused agent deployment:
1. Create sub-plan: `drone @flow create . "Phase X: [name]"`
2. Write agent instructions in sub-plan
3. Deploy agent with single-task focus
4. Review agent output (don't rebuild yourself)
5. Seedgo checklist on new code
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
- Follow Seedgo standards (3-layer architecture: apps/modules/handlers)
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

### Phase 1: Template Restructure + Class Registry
- [ ] Sub-plan created: FPLAN-____
- [ ] Agent deployed
- [ ] Agent completed
- [ ] Output reviewed
- [ ] Seedgo checklist passed
- [ ] Sub-plan closed
- [ ] Memories updated
- [ ] Email sent to @devpulse
- **Status:** Pending
- **Notes:**

### Phase 2: Passport Command + Class-Aware Create
- [ ] Sub-plan created: FPLAN-____
- [ ] Agent deployed
- [ ] Agent completed
- [ ] Output reviewed
- [ ] Seedgo checklist passed
- [ ] Sub-plan closed
- [ ] Memories updated
- [ ] Email sent to @devpulse
- **Status:** Pending
- **Notes:**

### Phase 3: Class-Aware Update + Profile Check
- [ ] Sub-plan created: FPLAN-____
- [ ] Agent deployed
- [ ] Agent completed
- [ ] Output reviewed
- [ ] Seedgo checklist passed
- [ ] Sub-plan closed
- [ ] Memories updated
- [ ] Email sent to @devpulse
- **Status:** Pending
- **Notes:**

### Phase 4: Integration Testing + Seedgo Compliance
- [ ] Sub-plan created: FPLAN-____
- [ ] Agent deployed
- [ ] Agent completed
- [ ] Output reviewed
- [ ] Seedgo checklist passed
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
- [ ] Full branch audit: `drone @seedgo audit @branch`
- [ ] Branch memories updated:
  - [ ] `BRANCH.local.json` - full session log
  - [ ] `BRANCH.observations.json` - patterns learned
- [ ] README.md updated (status, architecture, API - if build changed capabilities)
- [ ] Artifacts reviewed (devpulse manages cleanup)
- [ ] Final email to @devpulse:
  ```bash
  drone @ai_mail send @devpulse "FPLAN-0009 MASTER COMPLETE" "Full build summary: phases completed, deliverables, remaining issues (if any)"
  ```

**Completion Order:** Memories → README → Email (README before email - don't report complete with stale docs)

**Note:** Devpulse will perform its own Seedgo audit for visibility into the work.

### Definition of Done
1. `templates/` has `builder/` and `birthright/` (no more `agent.template/`)
2. `drone @spawn passport @daemon` creates .trinity/ + .aipass/ + registry entry
3. `drone @spawn create builder @path` creates full scaffold
4. `drone @spawn create @path` defaults to builder (backward compat)
5. `drone @spawn update builder --all` only touches builders
6. `drone @spawn update --all` blocked with clear error
7. All 10 existing passports have `citizen_class: "builder"`
8. daemon has `citizen_class: "birthright"` after passport command
9. All tests passing (84+ existing + new class tests)
10. Seedgo audit score maintained

---

## Close Command

When ALL phases complete and checklist done:
```bash
drone @flow close FPLAN-0009
```
