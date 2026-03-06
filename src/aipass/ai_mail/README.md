# ai_mail

Inter-agent messaging for AIPass. File-based email system that lets agents send, receive, and process messages using `@branch` addresses. No SMTP, no external services — just JSON files and symbolic routing.

**Status:** Building. Core email workflow (send/inbox/reply/close) is functional. Dispatch system is working.

## Usage

### CLI (via drone)

```bash
# Send a message
drone @ai_mail send @flow "Bug Report" "Found an issue in plan closing"

# Check inbox
drone @ai_mail inbox

# View a message (marks as opened)
drone @ai_mail view <message_id>

# Reply (auto-closes original)
drone @ai_mail reply <message_id> "Fixed in v2.1"

# Close without reply
drone @ai_mail close <message_id>

# Send with dispatch flag (recipient auto-executes the task)
drone @ai_mail send @flow "Task" "Details here" --dispatch
```

### Python

```python
from aipass.ai_mail.apps.modules.email import handle_command

# Module interface — all commands go through handle_command
handle_command(["send", "@flow", "Subject", "Message body"])
handle_command(["inbox"])
```

## Email Lifecycle

Messages follow a 3-state model:

```
new → opened → closed
```

- **new** — Delivered to inbox, never viewed
- **opened** — Viewed by recipient, awaiting action
- **closed** — Replied or dismissed, archived automatically

## Dispatch System

The `--dispatch` flag marks emails for autonomous execution. A polling daemon watches inboxes and spawns agents to process dispatch emails automatically.

- Agents are ephemeral (wake, do work, exit)
- Safety limits: max turns per wake, max dispatches per branch per day
- PID-based locking prevents concurrent agents per branch
- Failed agents trigger bounce emails back to sender

## Architecture

Follows the standard AIPass 3-layer pattern:

```
ai_mail/
├── apps/
│   ├── ai_mail.py          # Entry point (auto-discovers modules)
│   ├── modules/
│   │   ├── email.py        # Send, inbox, view, reply, close, contacts
│   │   ├── dispatch.py     # Dispatch status, daemon, wake
│   │   └── branch_ping.py  # Branch health monitoring
│   └── handlers/
│       ├── email/           # Delivery, formatting, inbox ops, purge
│       ├── dispatch/        # Daemon, wake, monitoring
│       ├── registry/        # Branch registry read/update
│       └── users/           # Branch detection, config generation
```

## Dependencies

- `prax` — Logging
- `cli` — Display formatting
- `drone` — Command routing and `@branch` resolution
