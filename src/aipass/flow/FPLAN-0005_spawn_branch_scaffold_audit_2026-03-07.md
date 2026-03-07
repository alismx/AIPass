# FPLAN-0005 - Spawn Branch Scaffold Audit

**Created**: 2026-03-07
**Branch**: flow
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
- **Status updates** - Quick progress lines so the user can glance without asking
- **Questions for the user** - Non-urgent questions that can wait for the next check-in
- **Notes to self** - Decisions made, things to revisit, gotchas discovered

Update it as you work - lightweight, not formal. The user checks it when they want to, skips it when busy.

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
drone @ai_mail send @devpulse "Subject" "Message"
drone @ai_mail --help                  # Full help

# Discovery
drone systems                          # All available modules
drone list @branch                     # Commands for branch
```

---

## Planning Phase

### Goal
All 10 branches are fully scaffolded citizens — each has `.trinity/` identity, `.aipass/` prompt, `.ai_mail.local/` mailbox, and all standard dirs from the spawn template. No code is overwritten — only missing pieces are added.

### Current State (Audit)

| Branch | .trinity/ | .aipass/ | .ai_mail.local/ | logs/ | Status |
|--------|:---------:|:--------:|:---------------:|:-----:|--------|
| **spawn** | YES | YES | YES | YES | COMPLETE |
| **devpulse** | YES | YES | YES | YES | COMPLETE |
| **ai_mail** | YES | MISSING | MISSING | YES | PARTIAL |
| **flow** | MISSING | MISSING | MISSING | YES | NEEDS SCAFFOLD |
| **prax** | MISSING | MISSING | MISSING | YES | NEEDS SCAFFOLD |
| **seedgo** | MISSING | MISSING | MISSING | YES | NEEDS SCAFFOLD |
| **trigger** | MISSING | MISSING | MISSING | YES | NEEDS SCAFFOLD |
| **api** | MISSING | MISSING | MISSING | MISSING | NEEDS SCAFFOLD |
| **cli** | MISSING | MISSING | MISSING | MISSING | NEEDS SCAFFOLD |
| **drone** | MISSING | MISSING | MISSING | MISSING | NEEDS SCAFFOLD |

### Approach
Deploy agents (one or more per branch) to add missing scaffold. Each agent:
1. Reads spawn's template (`src/aipass/spawn/templates/agent.template/`) to understand the standard
2. Reads the target branch to see what already exists
3. Adds ONLY what's missing — never overwrites existing files
4. Fills `.trinity/passport.json` with correct branch name, role, email (@name)
5. Creates stub `.aipass/branch_system_prompt.md` with branch-specific context
6. Sets up `.ai_mail.local/` mailbox structure

**Critical:** Existing code in `apps/`, `README.md`, etc. must NOT be touched. This is additive only.

### Reference Documents
- Template source: `src/aipass/spawn/templates/agent.template/`
- Mock example: `src/aipass/spawn/templates/agent_mock_branch/`
- Registry: `AIPASS_REGISTRY.json` (branch emails, paths, roles)
- Completed examples: `src/aipass/spawn/` and `src/aipass/devpulse/` (reference citizens)

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
- CROSS-BRANCH: Never modify other branches' files unless explicitly authorized by the user
- 2-ATTEMPT RULE: If something fails twice, note the issue and move on
- Do NOT go down rabbit holes debugging

WHEN COMPLETE:
- Verify code runs without syntax errors
- List files created/modified
- Note any issues encountered (with what was attempted)
```

---

## Execution Log

### 2026-03-07
- [ ] Created FPLAN-0005
- [ ] Agent deployed for: [task]
- [ ] Agent completed: [outcome]
- [ ] Seed checklist passed: [file]
- [ ] Memories updated

**Log Pattern:** Task → Agent → Outcome → Quality check → Next

**If production stops (critical blocker):**
```bash
drone @ai_mail send @devpulse "PRODUCTION STOPPED: FPLAN-0005" "Issue: [description]. Attempted: [what was tried]. Awaiting guidance."
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
- [ ] Status email sent to @devpulse:
  ```bash
  drone @ai_mail send @devpulse "FPLAN-0005 Complete" "Summary of what was done, any issues, outcomes"
  ```

**Completion Order:** Memories → README → Email (README before email - don't report complete with stale docs)

### Definition of Done
All 10 branches have: `.trinity/passport.json`, `.trinity/local.json`, `.trinity/observations.json`, `.aipass/branch_system_prompt.md`, `.ai_mail.local/inbox.json`, `logs/` directory. No existing code was overwritten. `drone @seedgo audit aipass` shows improvement across the board.

---

## Close Command

When all boxes checked:
```bash
drone @flow close FPLAN-0005
```
