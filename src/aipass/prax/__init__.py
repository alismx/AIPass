"""AIPass Prax — Visibility & Monitoring Layer.

Project-scoped logging, monitoring, and observability for AI agent ecosystems.
Depends on: aipass-paths, watchdog.

Internal Prax has 10 subsystems. The public version ships with 4 non-negotiable
trust changes:
    1. No global logging.getLogger() override — users call prax.logger() explicitly
    2. Project-scoped only — never operates outside the project directory
    3. All external communication opt-in — zero external by default
    4. Consent layer — prax init / prax status / prax stop (through drone)

Three modes:
    - Public:  Safe defaults. Minimal, transparent, project-scoped.
    - Full:    Opt-in power features (file watcher, log tailing, Telegram relay).
    - AIPass:  Internal unchanged (not shipped publicly).

Other modules don't configure Prax — they import correctly and use
warning(), info(), error() methods. Prax manages himself internally.

Architecture reference: vera/projects/framework/architecture_reference.md §6

Status: PLACEHOLDER — not yet implemented.
"""
