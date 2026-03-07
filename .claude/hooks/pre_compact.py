#!/usr/bin/env python3
"""
Pre-Compact Hook - Inject post-compact recovery instructions.

After compaction, Claude loses conversational flow and can come out
disoriented. This hook injects recovery instructions into the summary
to maintain conversational continuity.

Version: 1.0.0
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
The user may notice a tone shift. Handle this smoothly.

CONVERSATIONAL CONTINUITY (HIGHEST PRIORITY):
1. ACKNOWLEDGE if the user notices - be honest that compaction happened
2. MATCH THE TONE from the summary - if it was casual/brainstorming, stay casual
3. CONTINUE THE FLOW - pick up where the conversation left off naturally
4. DON'T pivot to new topics or ask generic questions
5. If you were mid-brainstorm, keep brainstorming. If mid-task, keep working.
6. DO NOT surface old notes/TODOs as if they're fresh conversation starters

PROCESS GUARDRAILS:
- If a planning/design discussion was active: continue it, don't start executing
- If mid-execution: continue if context is clear, ask if uncertain
- If a task was requested but not started: confirm before executing
- Delegation: if about to debug/code in another branch's domain, delegate via ai_mail

DEFAULT: Continue naturally. If genuinely uncertain, ask briefly - don't monologue about what you lost.""", file=sys.stdout)

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
