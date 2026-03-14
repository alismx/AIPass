# AIPass — Project Prompt

Project-level instructions. Persists in context for the entire conversation.

## Startup

On any greeting, silently read these files from CWD and run the commands — no narration, no announcing steps. Just do it and respond with the status.

**Read:** `.trinity/passport.json`, `.trinity/local.json`, `.trinity/observations.json`, `README.md`
**Run:** `git status`

## Memories

Update `.trinity/` at natural breakpoints, after milestones, and on `/memo`. If compaction hits before you save, it's gone.
