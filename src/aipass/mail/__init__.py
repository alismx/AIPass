"""AIPass Mail — Inter-Branch Messaging.

Communication layer for AI agent ecosystems. Branches coordinate through
email, not direct file access. This is how 10+ agents work simultaneously
without stepping on each other.

Each branch has a mailbox (BRANCHNAME.ai_mail.json). Mail supports:
    - send/receive between branches
    - dispatch flags (--dispatch marks for autonomous execution)
    - inbox/outbox management
    - reply chains with auto-close and archival

Integration requirement: branches register in BRANCH_REGISTRY.json
to be addressable. Seed enforces this.

Depends on: aipass-paths.

Architecture reference: vera/projects/framework/architecture_reference.md §8

Status: PLACEHOLDER — not yet implemented.
"""
