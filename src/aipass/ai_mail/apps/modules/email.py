
# ===================AIPASS====================
# META DATA HEADER
# Name: email.py - Email Orchestration Module
# Date: 2025-12-02
# Version: 2.2.0
# Category: ai_mail/modules
#
# CHANGELOG (Max 5 entries):
#   - v2.2.0 (2026-02-25): FPLAN-0373 Phase 2 - enriched dashboard write-through via push_dashboard_update
#   - v2.1.0 (2026-02-25): Add --no-memory-save flag for private branch outbound dispatch
#   - v2.0.0 (2026-02-16): Group send support - multiple @recipients parsed correctly with --dispatch
#   - v1.9.0 (2026-02-14): Batch close perf fix - defer dashboard/purge to single call after loop
#   - v1.8.0 (2026-02-08): Fix dispatch_target identity mismatch - use registry lookup instead of folder name
#
# CODE STANDARDS:
#   - Orchestration only - NO business logic
#   - Imports from handlers/ for all operations
#   - Uses json_handler.log_operation()
#   - 135-200 lines target (handles multiple workflows)
# =============================================

"""
Email Orchestration Module

Orchestrates email workflows for AI_Mail CLI system.
Handles: send, inbox, sent, contacts commands.

Module Pattern:
- handle_command(command, args) -> bool entry point
- Imports handlers for business logic
- Logs operations via json_handler
- NO business logic in this file
"""

import sys
import argparse
from pathlib import Path
from typing import List

# Infrastructure (package-relative)
_AI_MAIL_DIR = Path(__file__).resolve().parents[2]  # ai_mail/

from aipass.prax.apps.modules.logger import system_logger as logger
from aipass.cli.apps.modules import console
from aipass.ai_mail.apps.handlers.email.dashboard_sync import push_dashboard_update

try:
    from aipass.ai_mail.apps.handlers.central_writer import update_central
except ImportError:
    update_central = None

try:
    from aipass.devpulse.apps.modules.dashboard import update_section as _update_dashboard_section
except ImportError:
    _update_dashboard_section = None

# Import handlers (business logic providers)
from aipass.ai_mail.apps.handlers.email.delivery import deliver_email_to_branch
from aipass.ai_mail.apps.handlers.email.create import create_email_file, load_email_file
from aipass.ai_mail.apps.handlers.email.format import format_email_preview, format_email_header, format_email_list_item
from aipass.ai_mail.apps.handlers.email.inbox_ops import load_inbox
from aipass.ai_mail.apps.handlers.email.inbox_cleanup import (
    mark_read_and_archive, mark_all_read_and_archive,
    mark_as_opened, mark_as_closed_and_archive
)
from aipass.ai_mail.apps.handlers.email.reply import get_email_by_id, send_reply
from aipass.ai_mail.apps.handlers.email.header import prepend_dispatch_header
from aipass.ai_mail.apps.handlers.users.user import get_current_user
from aipass.ai_mail.apps.handlers.registry.read import get_all_branches, get_branch_by_email
from aipass.ai_mail.apps.handlers.json_utils.json_handler import log_operation


def _on_email_delivered(branch_path, new_count, opened_count, total):
    """Post-delivery callback: update dashboard (enriched) and central."""
    try:
        push_dashboard_update(branch_path)
    except Exception:
        pass  # Dashboard update is best-effort
    try:
        update_central()
    except Exception:
        pass  # Central update is best-effort


def _dispatch_send_error(to_branch: str, subject: str, error_msg: str) -> None:
    """
    Auto-dispatch error report to @drone when email delivery fails.

    Args:
        to_branch: Intended recipient that failed
        subject: Original email subject
        error_msg: Error message from delivery failure
    """
    try:
        from datetime import datetime

        user_info = get_current_user()
        sender = user_info.get("email_address", "@ai_mail")

        error_report = (
            f"Email delivery failed.\n\n"
            f"From: {sender}\n"
            f"To: {to_branch}\n"
            f"Subject: {subject}\n"
            f"Error: {error_msg}\n\n"
            f"This error was auto-dispatched for investigation."
        )

        email_data = {
            "from": "@ai_mail",
            "from_name": "AI_MAIL",
            "to": "@drone",
            "subject": f"[ERROR] Send failed to {to_branch}: {error_msg[:50]}",
            "message": error_report,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "auto_execute": False,
            "priority": "normal",
            "reply_to": "@dev_central"
        }

        deliver_email_to_branch("@drone", email_data)
        logger.info(f"[email] Error auto-dispatched to @drone for failed send to {to_branch}")

    except Exception as e:
        logger.warning(f"[email] Failed to dispatch send error to @drone: {e}")


def print_introspection():
    """Display module info and connected handlers"""
    console.print()
    console.print("[bold cyan]Email Orchestration Module[/bold cyan]")
    console.print()
    console.print("[dim]Orchestrates email workflows (send, inbox, sent, contacts)[/dim]")
    console.print()

    console.print("[yellow]Connected Handlers:[/yellow]")
    console.print()
    console.print("  [cyan]email/[/cyan]")
    console.print("    [dim]- delivery.py (deliver_email_to_branch)[/dim]")
    console.print("    [dim]- create.py (create_email_file, load_email_file)[/dim]")
    console.print("    [dim]- format.py (format_email_*)[/dim]")
    console.print("    [dim]- inbox_ops.py (load_inbox)[/dim]")
    console.print()
    console.print("  [cyan]users/[/cyan]")
    console.print("    [dim]- user.py (get_current_user)[/dim]")
    console.print()
    console.print("  [cyan]registry/[/cyan]")
    console.print("    [dim]- read.py (get_all_branches, get_branch_by_email)[/dim]")
    console.print()
    console.print("  [cyan]persistence/[/cyan]")
    console.print("    [dim]- json_ops.py (log_operation)[/dim]")
    console.print()
    console.print("[dim]Run 'python3 email.py --help' for usage[/dim]")
    console.print()


def print_help():
    """Print drone-compliant help output"""
    help_text = """
Email Module - Send and manage branch-to-branch email (Lifecycle v2)

COMMANDS:
  send      - Send email to a branch
  inbox     - View inbox messages (new + opened)
  view      - View email content and mark as opened
  reply     - Reply to email (auto-closes original)
  close     - Close email without reply (archives to deleted)
  sent      - View sent messages
  contacts  - Manage contacts
  read      - (Alias for 'view' - backward compatibility)

EMAIL LIFECYCLE (v2):
  new → opened → closed → deleted

  1. Email arrives with status: "new"
  2. Use 'view <id>' to read content (marks as "opened")
  3. Use 'reply <id> "msg"' to respond (auto-closes + archives)
     OR 'close <id>' to close without reply (archives to deleted)

USAGE:
  ai_mail send @recipient "subject" "message" [--dispatch] [--reply-to @branch]
  ai_mail inbox
  ai_mail view <message_id>            # View and mark as opened
  ai_mail reply <message_id> "msg"     # Reply and close original
  ai_mail close <message_id>           # Close without reply
  ai_mail sent
  ai_mail contacts

FLAGS:
  --dispatch        Spawn Claude agent at target branch to execute the email task.
                    Use when recipient needs to ACT (tasks, bugs, requests).
                    Skip when just informing (acks, ideas, status updates).
  --reply-to        Redirect replies to a different branch (e.g., --reply-to @dev_central)
  --auto-execute    (Alias for --dispatch - backward compatibility)

EXAMPLES:
  # Send informational email (no agent spawn)
  ai_mail send @seed "Status Update" "All checks passing"

  # Dispatch task to branch (spawns agent to execute)
  ai_mail send @drone "Task: Update config" "Please update X" --dispatch

  # Broadcast announcement (no dispatch - informational)
  ai_mail send @all "Announcement" "System update tonight"

  # View inbox (shows new + opened emails)
  ai_mail inbox

  # View email content (marks as opened)
  ai_mail view a7b3c9d2

  # Reply to email (sends reply + closes original)
  ai_mail reply a7b3c9d2 "Thanks, I'll review this today"

  # Close email without replying
  ai_mail close a7b3c9d2

  # View sent messages
  ai_mail sent

  # View all branches
  ai_mail contacts

WHEN TO USE --dispatch:
  ✓ Task assignments     - "Task: Fix the bug in X"
  ✓ Action requests      - "Please review and merge PR #123"
  ✓ Bug reports          - "BUG: Feature Y is broken"
  ✗ Status updates       - "Complete: Task X finished"
  ✗ Acknowledgments      - "Received, will review tomorrow"
  ✗ Ideas/proposals      - "IDEA: Consider approach Z"
"""
    console.print(help_text)


def handle_command(command: str, args: List[str]) -> bool:
    """
    Handle email commands

    Args:
        command: Command name (send, inbox, sent, contacts)
        args: Command arguments

    Returns:
        True if command handled, False otherwise
    """
    # Check if this module handles this command
    if command not in ["send", "inbox", "view", "close", "reply", "sent", "contacts", "read"]:
        return False

    # Handle --help flag in args
    if args and args[0] in ['--help', '-h', 'help']:
        print_help()
        return True

    # Route to appropriate workflow
    if command == "send":
        return handle_send(args)
    elif command == "inbox":
        return handle_inbox(args)
    elif command == "view":
        return handle_view(args)
    elif command == "close":
        return handle_close(args)
    elif command == "reply":
        return handle_reply(args)
    elif command == "read":
        # Backward compat: read now behaves like view
        return handle_view(args)
    elif command == "sent":
        return handle_sent(args)
    elif command == "contacts":
        return handle_contacts(args)
    else:
        return False


def handle_send(args: List[str]) -> bool:
    """Orchestrate email sending workflow"""
    log_operation("send_email_initiated", {"args_count": len(args)})

    # Check for --dispatch or --auto-execute flag (--dispatch is the new canonical name)
    auto_execute = '--dispatch' in args or '--auto-execute' in args
    if auto_execute:
        args = [a for a in args if a not in ('--dispatch', '--auto-execute')]

    # Check for --no-memory-save flag (private branch outbound: skip memory logging at recipient)
    no_memory_save = '--no-memory-save' in args
    if no_memory_save:
        args = [a for a in args if a != '--no-memory-save']

    # Check for --reply-to flag
    reply_to = None
    if '--reply-to' in args:
        idx = args.index('--reply-to')
        if idx + 1 < len(args):
            reply_to = args[idx + 1]
            args = args[:idx] + args[idx + 2:]
        else:
            console.print("❌ --reply-to requires a branch address (e.g., --reply-to @dev_central)")
            return False

    # Separate recipients (@-prefixed) from subject/message
    recipients = []
    rest = []
    for a in args:
        if a.startswith('@') and not rest:
            recipients.append(a)
        elif a.startswith('/') and not rest:
            # Path-based recipient (e.g., /path/to/branch)
            recipients.append(a)
        else:
            rest.append(a)

    # Direct send mode: send @recipient(s) "subject" "message"
    if recipients and len(rest) >= 2:
        subject = rest[0]
        message = rest[1]

        def _resolve_dispatch_target(branch: str) -> str | None:
            """Resolve dispatch target for a single recipient"""
            if not auto_execute:
                return None
            if branch.startswith('/') or branch.startswith('~'):
                from aipass.ai_mail.apps.handlers.users.branch_detection import get_branch_info_from_registry
                branch_info = get_branch_info_from_registry(Path(branch))
                if branch_info:
                    return branch_info.get("email", f"@{Path(branch).name.lower()}")
                return f"@{Path(branch).name.lower()}"
            return branch

        # Single recipient - original behavior
        if len(recipients) == 1:
            dispatch_target = _resolve_dispatch_target(recipients[0])
            return send_email_direct(recipients[0], subject, message, auto_execute=auto_execute, reply_to=reply_to, dispatched_to=dispatch_target, no_memory_save=no_memory_save)

        # Multiple recipients - send to each
        console.print(f"\n📨 Group send to {len(recipients)} recipients...")
        success_count = 0
        for recipient in recipients:
            dispatch_target = _resolve_dispatch_target(recipient)
            success = send_email_direct(recipient, subject, message, auto_execute=auto_execute, reply_to=reply_to, dispatched_to=dispatch_target, no_memory_save=no_memory_save)
            if success:
                success_count += 1
        console.print(f"\n📊 Group send complete: {success_count}/{len(recipients)} delivered")
        return success_count > 0

    # Interactive send mode
    elif not recipients and not rest:
        return send_email_interactive()

    # Bad args - not enough info
    else:
        console.print("❌ Usage: send @recipient [subject] [message]")
        console.print("   Multiple: send @branch1 @branch2 \"Subject\" \"Message\"")
        return False


def send_email_interactive() -> bool:
    """Interactive email sending with prompts"""
    branches = get_all_branches()

    console.print("\n📧 AI_Mail - Send Email")
    console.print("=" * 50)

    # Show branch selection
    console.print("\nSelect recipient:")
    for i, branch in enumerate(branches, 1):
        console.print(f"  {i}. {branch['name']} ({branch['email']})")
    console.print(f"  {len(branches) + 1}. ALL BRANCHES (broadcast)")

    # Get selection
    try:
        selection = input(f"\nPick (1-{len(branches) + 1}): ").strip()
        idx = int(selection) - 1

        if idx == len(branches):
            selected_email = "all"
        elif idx < 0 or idx >= len(branches):
            console.print("❌ Invalid selection")
            return False
        else:
            selected_email = branches[idx]["email"]
    except (ValueError, KeyboardInterrupt, EOFError):
        console.print("\n❌ Cancelled")
        return False

    # Get subject
    try:
        subject = input("Subject: ").strip()
        if not subject:
            console.print("❌ Subject cannot be empty")
            return False
    except (KeyboardInterrupt, EOFError):
        console.print("\n❌ Cancelled")
        return False

    # Get message
    console.print("Message (press Ctrl+D when done, Ctrl+C to cancel):")
    try:
        message_lines = []
        while True:
            try:
                line = input()
                message_lines.append(line)
            except EOFError:
                break
        message = "\n".join(message_lines).strip()
        if not message:
            console.print("❌ Message cannot be empty")
            return False
    except KeyboardInterrupt:
        console.print("\n❌ Cancelled")
        return False

    # Confirm send
    console.print("\n" + "=" * 50)
    console.print(f"To: {selected_email}")
    console.print(f"Subject: {subject}")
    console.print(f"Message:\n{message}")
    console.print("=" * 50)

    try:
        confirm = input("\nSend? (y/n): ").strip().lower()
        if confirm != 'y':
            console.print("❌ Cancelled")
            return False
    except (KeyboardInterrupt, EOFError):
        console.print("\n❌ Cancelled")
        return False

    return send_email_direct(selected_email, subject, message)


def send_email_direct(to_branch: str, subject: str, message: str, auto_execute: bool = False, reply_to: str | None = None, dispatched_to: str | None = None, from_branch: str | None = None, no_memory_save: bool = False) -> bool:
    """Direct email sending (orchestrates handlers)

    Args:
        to_branch: Recipient email address (e.g., @flow)
        subject: Email subject
        message: Email body
        auto_execute: If True, spawn agent at recipient branch
        reply_to: Optional branch to redirect replies to
        dispatched_to: Track dispatch target for reply validation
        from_branch: Optional sender override (e.g., @trigger). If None, uses PWD detection.
        no_memory_save: If True, add no-memory-save directive to dispatch header
    """
    try:
        # Get sender info - use explicit from_branch if provided, otherwise detect from PWD
        if from_branch:
            # Normalize email format (handle @trigger or trigger formats)
            email_addr = f"@{from_branch.lstrip('@').lower()}"
            # Look up branch from registry to get correct path
            branch_info = get_branch_by_email(email_addr)
            if branch_info:
                branch_path = Path(branch_info["path"])
                user_info = {
                    "email_address": email_addr,
                    "display_name": branch_info["name"],
                    "mailbox_path": str(branch_path / ".ai_mail.local"),
                    "timestamp_format": "%Y-%m-%d %H:%M:%S"
                }
            else:
                # Fallback for unregistered branches (shouldn't happen in production)
                branch_name = from_branch.lstrip('@').upper()
                user_info = {
                    "email_address": email_addr,
                    "display_name": branch_name,
                    "mailbox_path": str(_AI_MAIL_DIR.parent / from_branch.lstrip('@').lower() / ".ai_mail.local"),
                    "timestamp_format": "%Y-%m-%d %H:%M:%S"
                }
        else:
            user_info = get_current_user()

        # Prepend dispatch header for auto-execute emails (critical memory update reminder)
        if auto_execute:
            message = prepend_dispatch_header(message, no_memory_save=no_memory_save)

        # Broadcast mode
        if to_branch.lower() in ['all', '@all']:
            branches = get_all_branches()
            success_count = 0

            # Create email file (pass reply_to, dispatched_to for broadcast)
            email_file = create_email_file("all", subject, message, user_info, reply_to=reply_to, dispatched_to=dispatched_to)
            email_data = load_email_file(email_file)

            # Handle None case (file not found/couldn't be loaded)
            if email_data is None:
                console.print("❌ Failed to load email file for broadcast")
                log_operation("broadcast_failed", {"error": "Email file could not be loaded"})
                return False

            console.print(f"\n📢 Broadcasting to {len(branches)} branches...")

            # Deliver to each branch
            for branch in branches:
                delivery_data = email_data.copy()
                delivery_data['to'] = branch['email']
                delivery_data['auto_execute'] = auto_execute
                if no_memory_save:
                    delivery_data['no_memory_save'] = True

                success, error_msg = deliver_email_to_branch(branch['email'], delivery_data, on_delivered=_on_email_delivered)
                if success:
                    success_count += 1
                    console.print(f"  ✅ {branch['name']}")
                else:
                    console.print(f"  ❌ {branch['name']} ({error_msg})")

            console.print(f"\n📊 Broadcast complete: {success_count}/{len(branches)} delivered")
            log_operation("broadcast_sent", {"recipients": len(branches), "successful": success_count})

            # Fire trigger event
            try:
                from aipass.trigger.apps.modules.core import trigger
                trigger.fire('email_broadcast_sent', recipients=len(branches), successful=success_count, subject=subject)
            except ImportError:
                pass  # Silent fallback if trigger unavailable

            # Update central after broadcast
            try:
                update_central()
            except Exception:
                pass  # Don't break mail ops if central update fails

            return success_count > 0

        # Single recipient
        else:
            email_file = create_email_file(to_branch, subject, message, user_info, reply_to=reply_to, dispatched_to=dispatched_to)
            email_data = load_email_file(email_file)

            # Handle None case (file not found/couldn't be loaded)
            if email_data is None:
                console.print(f"❌ Failed to load email file")
                log_operation("email_failed", {"to": to_branch, "error": "Email file could not be loaded"})
                return False

            # Add auto_execute flag, dispatch tracking, and memory directive
            email_data['auto_execute'] = auto_execute
            if dispatched_to:
                email_data['dispatched_to'] = dispatched_to
            if no_memory_save:
                email_data['no_memory_save'] = True

            success, error_msg = deliver_email_to_branch(to_branch, email_data, on_delivered=_on_email_delivered)

            if success:
                if auto_execute:
                    console.print(f"✅ Email sent to {to_branch} \\[dispatch: queued for daemon]")
                else:
                    console.print(f"✅ Email sent to {to_branch}")
                log_operation("email_sent", {"to": to_branch, "subject": subject, "auto_execute": auto_execute})

                # Fire trigger event
                try:
                    from aipass.trigger.apps.modules.core import trigger
                    trigger.fire('email_sent', to=to_branch, subject=subject, auto_execute=auto_execute)
                except ImportError:
                    pass  # Silent fallback if trigger unavailable

                # Update central after send
                try:
                    update_central()
                except Exception:
                    pass  # Don't break mail ops if central update fails

                return True
            else:
                console.print(f"❌ Failed to deliver: {error_msg}")
                log_operation("email_failed", {"to": to_branch, "error": error_msg})
                _dispatch_send_error(to_branch, subject, error_msg)
                return False

    except BrokenPipeError:
        logger.info("[email] Send: broken pipe (stdout closed early)")
        return True
    except Exception as e:
        logger.error(f"[email] Send failed: {e}")
        console.print(f"❌ Error: {e}")
        _dispatch_send_error(to_branch, subject, str(e))
        return False


def handle_inbox(args: List[str]) -> bool:
    """Orchestrate inbox viewing workflow.

    Usage:
        inbox           - View current branch's inbox (detected from PWD)
        inbox @branch   - View specified branch's inbox
    """
    log_operation("inbox_viewed")

    try:
        # Check if a target branch was specified
        target_branch = None
        if args and args[0].startswith("@"):
            target_branch = args[0]

        if target_branch:
            # Look up target branch from registry
            branch_info = get_branch_by_email(target_branch)
            if not branch_info:
                console.print(f"❌ Unknown branch: {target_branch}")
                return False
            branch_path = Path(branch_info["path"])
            mailbox_path = branch_path / ".ai_mail.local"
            display_name = branch_info.get("name", target_branch)
        else:
            # Use current branch (detected from PWD)
            user_info = get_current_user()
            mailbox_path = Path(user_info["mailbox_path"])
            display_name = user_info.get("display_name", "")

        inbox_file = mailbox_path / "inbox.json"

        if not inbox_file.exists():
            if target_branch:
                console.print(f"📭 {target_branch} inbox is empty")
            else:
                console.print("📭 Inbox is empty")
            return True

        # Load inbox using handler
        inbox_data = load_inbox(inbox_file)
        messages = inbox_data.get("messages", [])

        if not messages:
            if target_branch:
                console.print(f"📭 {target_branch} inbox is empty")
            else:
                console.print("📭 Inbox is empty")
            return True

        # Display messages (newest first)
        messages_display = list(reversed(messages))[:20]

        if target_branch:
            console.print(f"\n📬 Inbox for {target_branch} ({display_name})")
        else:
            console.print("\n📬 Inbox")
        console.print("=" * 70)

        for i, msg in enumerate(messages_display, 1):
            console.print(format_email_list_item(i, msg, show_unread=True))

        console.print("\n" + "=" * 70)
        console.print(f"Showing {len(messages_display)} of {len(messages)} messages")
        console.print("\n[dim]To archive: drone @ai_mail read <message_id> or drone @ai_mail read all[/dim]")

        return True

    except BrokenPipeError:
        logger.info("[email] Inbox view: broken pipe (stdout closed early)")
        return True
    except Exception as e:
        logger.error(f"[email] Inbox view failed: {e}")
        console.print(f"❌ Error: {e}")
        return False


def handle_read(args: List[str]) -> bool:
    """Orchestrate email read/archive workflow"""
    log_operation("read_email_initiated", {"args": args})

    if not args:
        console.print("❌ Usage: drone @ai_mail read <message_id> or drone @ai_mail read all")
        return False

    try:
        user_info = get_current_user()
        # mailbox_path is .ai_mail.local/, branch_path is parent
        branch_path = Path(user_info["mailbox_path"]).parent

        # Archive all messages
        if args[0].lower() == "all":
            success, message, count = mark_all_read_and_archive(branch_path)
            if success:
                console.print(f"✅ {message}")
                log_operation("all_emails_archived", {"count": count})
            else:
                console.print(f"❌ {message}")
            return success

        # Archive single message
        else:
            message_id = args[0]
            success, message = mark_read_and_archive(branch_path, message_id)
            if success:
                console.print(f"✅ {message}")
                log_operation("email_archived", {"message_id": message_id})
            else:
                console.print(f"❌ {message}")
            return success

    except Exception as e:
        logger.error(f"[email] Read/archive failed: {e}")
        console.print(f"❌ Error: {e}")
        return False


def handle_view(args: List[str]) -> bool:
    """
    View email content and mark as opened (v2 schema).
    Does NOT archive - email stays in inbox with status: opened.
    """
    log_operation("view_email_initiated", {"args": args})

    if not args:
        console.print("❌ Usage: drone @ai_mail view <message_id>")
        return False

    try:
        user_info = get_current_user()
        branch_path = Path(user_info["mailbox_path"]).parent
        message_id = args[0]

        # Mark as opened and get email content
        success, message, email_data = mark_as_opened(branch_path, message_id)

        if not success:
            console.print(f"❌ {message}")
            return False

        # Display the email
        console.print("\n" + "="*60)
        console.print(f"📧 From: {email_data.get('from', 'unknown')} ({email_data.get('from_name', '')})")
        console.print(f"📌 Subject: {email_data.get('subject', 'No subject')}")
        console.print(f"🕐 {email_data.get('timestamp', '')}")
        console.print("="*60)
        console.print(f"\n{email_data.get('message', '')}\n")
        console.print("="*60)
        console.print(f"[dim]Status: opened | ID: {message_id}[/dim]")
        console.print(f"[dim]To reply: drone @ai_mail reply {message_id} \"your message\"[/dim]")
        console.print(f"[dim]To close: drone @ai_mail close {message_id}[/dim]")

        log_operation("email_viewed", {"message_id": message_id})
        return True

    except BrokenPipeError:
        logger.info("[email] View: broken pipe (stdout closed early)")
        return True
    except Exception as e:
        logger.error(f"[email] View failed: {e}")
        console.print(f"❌ Error: {e}")
        return False


def handle_close(args: List[str]) -> bool:
    """
    Close email(s) and archive to deleted (v2 schema).
    Marks status: closed and moves to deleted.json.

    Supports:
        close <id>              - Close single email
        close <id1> <id2> ...   - Close multiple emails
        close all               - Close all emails in inbox
    """
    log_operation("close_email_initiated", {"args": args})

    if not args:
        console.print("❌ Usage: drone @ai_mail close <id> [id2 id3 ...] | close all")
        return False

    try:
        user_info = get_current_user()
        branch_path = Path(user_info["mailbox_path"]).parent

        # Handle "close all"
        if args[0].lower() == "all":
            success, message, count = mark_all_read_and_archive(branch_path)
            if success:
                console.print(f"✅ {message}")
                log_operation("email_closed_all", {"count": count})
            else:
                console.print(f"❌ {message}")
            return success

        # Handle one or more message IDs
        # When closing multiple, defer dashboard/purge to single call after loop
        batch_mode = len(args) > 1
        closed_count = 0
        failed_count = 0
        for message_id in args:
            success, message = mark_as_closed_and_archive(branch_path, message_id, skip_post_ops=batch_mode)
            if success:
                console.print(f"✅ {message}")
                log_operation("email_closed", {"message_id": message_id})
                closed_count += 1
            else:
                console.print(f"❌ {message}")
                failed_count += 1

        # Run dashboard update + purge once after batch close
        if batch_mode and closed_count > 0:
            try:
                push_dashboard_update(branch_path)
                update_central()
            except Exception:
                pass  # Dashboard/central update is best-effort
            try:
                from aipass.ai_mail.apps.handlers.email.purge import purge_deleted_folder
                purge_deleted_folder(branch_path / ".ai_mail.local")
            except Exception:
                pass

        if batch_mode:
            console.print(f"\n📊 Closed {closed_count}, failed {failed_count}")

        return failed_count == 0

    except Exception as e:
        logger.error(f"[email] Close failed: {e}")
        console.print(f"❌ Error: {e}")
        return False


def handle_reply(args: List[str]) -> bool:
    """
    Reply to an email (v2 schema).
    Sends reply to original sender + auto-closes original.
    """
    log_operation("reply_email_initiated", {"args": args})

    if len(args) < 2:
        console.print("❌ Usage: drone @ai_mail reply <message_id> \"your message\"")
        return False

    try:
        user_info = get_current_user()
        branch_path = Path(user_info["mailbox_path"]).parent
        inbox_file = branch_path / ".ai_mail.local" / "inbox.json"

        message_id = args[0]
        reply_message = args[1]

        # Get original email
        original_email = get_email_by_id(inbox_file, message_id)
        if not original_email:
            console.print(f"❌ Message not found: {message_id}")
            return False

        # Send reply
        success, message, reply_id = send_reply(branch_path, original_email, reply_message)

        if success:
            console.print(f"✅ {message}")
            log_operation("email_replied", {"message_id": message_id, "reply_id": reply_id})
        else:
            console.print(f"❌ {message}")

        return success

    except Exception as e:
        logger.error(f"[email] Reply failed: {e}")
        console.print(f"❌ Error: {e}")
        return False


def handle_sent(args: List[str]) -> bool:
    """Orchestrate sent messages viewing workflow"""
    log_operation("sent_viewed")

    try:
        user_info = get_current_user()
        mailbox_path = Path(user_info["mailbox_path"])
        sent_folder = mailbox_path / "sent"

        if not sent_folder.exists():
            console.print("📭 No sent messages")
            return True

        # Get email files
        email_files = sorted(sent_folder.glob("*.json"), reverse=True)[:20]

        if not email_files:
            console.print("📭 No sent messages")
            return True

        console.print("\n📤 Sent Messages")
        console.print("=" * 70)

        for i, email_file in enumerate(email_files, 1):
            email_data = load_email_file(email_file)
            if email_data:
                console.print(format_email_list_item(i, email_data, show_unread=False))

        console.print("\n" + "=" * 70)
        console.print(f"Showing {len(email_files)} sent messages")

        return True

    except Exception as e:
        logger.error(f"[email] Sent view failed: {e}")
        console.print(f"❌ Error: {e}")
        return False


def handle_contacts(args: List[str]) -> bool:
    """Orchestrate contacts management workflow"""
    log_operation("contacts_viewed")

    try:
        branches = get_all_branches()

        if not branches:
            console.print("❌ No contacts found")
            return False

        console.print(f"\nTotal: {len(branches)} branches\n")
        console.print(f"{'EMAIL':<20} {'BRANCH NAME':<25} {'PATH':<35}")
        console.print("-" * 80)

        for branch in sorted(branches, key=lambda b: b["email"]):
            email = branch["email"]
            name = branch["name"]
            path = branch["path"]

            console.print(f"{email:<20} {name:<25} {path:<35}")

        return True

    except Exception as e:
        logger.error(f"[email] Contacts view failed: {e}")
        console.print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    # Show introspection when run without arguments
    if len(sys.argv) == 1:
        print_introspection()
        sys.exit(0)

    # Handle help flag
    if sys.argv[1] in ['--help', '-h', 'help']:
        print_help()
        sys.exit(0)

    # Execute command
    command = sys.argv[1]
    remaining_args = sys.argv[2:] if len(sys.argv) > 2 else []

    if handle_command(command, remaining_args):
        sys.exit(0)
    else:
        console.print()
        console.print(f"[red]Unknown command: {command}[/red]")
        console.print()
        console.print("Run [dim]python3 email.py --help[/dim] for available commands")
        console.print()
        sys.exit(1)
