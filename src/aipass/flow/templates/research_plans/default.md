# {plan_number}: {subject}

Tag: research, external-repo, {tag}

> One-line summary: what this repo/project does + why we're looking

---

## What is an RPLAN?

Research Plans (RPLANs) are **studying external work** -- analyzing repos, packages, libraries, projects to extract patterns, ideas, lessons that could benefit AIPass.

**This is for:**
- Analyzing external repo or pip package
- Documenting architecture, patterns, design decisions found
- Identifying what AIPass could learn or adapt
- Recording honest assessments -- what's good, what's not, what's relevant
- Preserving research so you don't repeat it next session

**This is NOT for:**
- Building code -- that's FPLAN
- Planning AIPass features -- that's DPLAN (create one if research inspires build)
- Quick glances -- if takes 5 minutes, just note in memories

**RPLANs live in external repo's root directory**, not in branch. When you revisit that repo later, research is right there waiting. RPLAN is artifact that makes research recoverable.

**Never trim RPLAN.** Raw findings, dead ends, "this looked promising but wasn't" -- all valuable. Future you will thank past you.

---

## Source

| Field | Value |
|-------|-------|
| **Repo/Package** | Name + source URL |
| **Installed via** | pip install / git clone / both |
| **Version analyzed** | Version number or commit hash |
| **License** | License type + notable restrictions |
| **Language** | Primary language(s) |
| **Size** | Approximate LOC or file count |
| **Local path** | Where it lives on disk |

## What It Does

High-level description. What problem does it solve? Who is it for? How does it work conceptually?

## Architecture

How codebase structured. Key directories, entry points, data flow. Include tree or diagram if helpful.

```
project/
├── core/          # What lives here
├── clients/       # What lives here
└── integrations/  # What lives here
```

## Key Files Analyzed

Each significant file reviewed:

### filename.py (LOC count)
- **Purpose:** What it does
- **Core pattern:** Main approach or algorithm
- **What's clever:** Notable design decisions
- **AIPass relevance:** How this could inform our work
- **Gotchas:** Limitations or issues noticed

*(Repeat each file worth documenting)*

## Patterns Worth Adopting

What did we find AIPass could learn? Be specific -- not "their memory is good" but "they use prefix-indexed keys like AGENT:id:STATE:type for O(k) queries, which could improve our ChromaDB tagging."

| Pattern | Where Found | AIPass Application | Priority |
|---------|-------------|-------------------|----------|
| Example pattern | file.py | How we'd use it | High/Med/Low |

## Patterns to Avoid

What we should NOT copy? Bad practices, overcomplicated approaches, things that don't fit our architecture.

## Honest Assessment

- **What they do better than us:**
- **What we do better than them:**
- **Overlap AIPass:**
- **Key differentiator:**

## Next Steps

- [ ] Create DPLAN if any patterns worth building
- [ ] Note findings in relevant branch memories
- [ ] Share relevant branches via dispatch if applicable

## Relationships
- **Related DPLANs:** Link any design plans this research inspired
- **Related branches:** Which AIPass branches would benefit
- **Discovered via:** How we found this project (recommendation, search, dependency, etc.)

## Notes
Session notes, raw observations, things noticed during research

## Listen (TTS-friendly summary)

Write a plain English summary of this research here. No markdown, no symbols, no tables, no code blocks, no asterisks, no bullet points. Just natural sentences that can be read aloud by a text to speech tool. Cover what the project is, what we found interesting, and what AIPass could learn from it.

---
*Created: {today}*
*Updated: {today}*
