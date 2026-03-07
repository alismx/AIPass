#!/usr/bin/env python3
"""
Pre-Compact Hook - Inject post-compact recovery instructions.

After compaction, Claude loses conversational flow and can come out
disoriented. This hook injects recovery instructions into the summary
to maintain conversational continuity.

Version: 2.0.0
"""

import sys
import json


def main():
    """Main hook entry point."""
    try:
        json.load(sys.stdin)

        print("Context compacting - recovery instructions injected", file=sys.stderr)

        print("""POST-COMPACT RECOVERY (MANDATORY):

You just compacted. You're working from a summary now, not live memory.

STEP 1 — RE-ORIENT (do this silently, don't narrate):
- Read .trinity/local.json — your active tasks, recent sessions, key learnings
- Read .trinity/observations.json — collaboration patterns with Patrick
- Check .ai_mail.local/inbox.json — any unread mail?
- Your passport and system prompts are already injected via hooks — don't re-read those.

STEP 2 — CONTINUE NATURALLY:
- Pick up where the conversation left off (the summary tells you where)
- Match the tone from before — if casual, stay casual
- Don't pivot to new topics or ask generic "what should we work on?" questions
- If mid-task: continue. If mid-discussion: continue. If uncertain: ask briefly.

GUARDRAILS:
- Don't monologue about what you lost or what compaction did
- Don't surface old TODOs as fresh conversation starters
- Delegate code work to sub-agents — you're a manager, protect your context
- If about to debug/code in another branch's domain, delegate via ai_mail""", file=sys.stdout)

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
