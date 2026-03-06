#!/home/aipass/.venv/bin/python3

# ===================AIPASS====================
# META DATA HEADER
# Name: footer.py - Email Footer Handler
# Date: 2026-01-29
# Version: 1.0.0
# Category: ai_mail/handlers/email
#
# CHANGELOG (Max 5 entries):
#   - v1.0.0 (2026-01-29): Created - auto-footer for all outgoing emails
#
# CODE STANDARDS:
#   - Handler independence: NO cross-domain imports
#   - Can import Prax modules (service providers)
#   - Pure business logic only
# =============================================

"""
Email Footer Handler

Generates and appends standard footer to all outgoing emails.
Reminds branches of process steps: Seed audit, memory update, FPLAN close, confirmation.
Independent handler - no module dependencies.
"""

# Standard footer for all outgoing emails
STANDARD_FOOTER = """
---
⚠️ TASK CHECKLIST (before marking complete):
□ SEED CHECK → drone @seed audit @branch (80%+)
□ UPDATE MEMORIES → Your .local.json records this work
□ CLOSE FPLAN → drone @flow close <plan_id>
□ CONFIRM → Reply with completion summary

Memories = Presence. No update = No learning.
---"""


def get_footer() -> str:
    """
    Get the standard email footer.

    Returns:
        Standard footer string for all outgoing emails
    """
    return STANDARD_FOOTER


def append_footer(message: str) -> str:
    """
    Append standard footer to email message.

    Args:
        message: Original email message body

    Returns:
        Message with footer appended
    """
    return message + get_footer()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("EMAIL FOOTER HANDLER")
    print("="*70)
    print("\nPURPOSE:")
    print("  Generates standard footer for all outgoing emails")
    print()
    print("FUNCTIONS PROVIDED:")
    print("  - get_footer() -> str")
    print("  - append_footer(message) -> str")
    print()
    print("FOOTER CONTENT:")
    print(STANDARD_FOOTER)
    print()
    print("HANDLER CHARACTERISTICS:")
    print("  ✓ Independent - no module dependencies")
    print("  ✓ Can import Prax (service provider)")
    print("  ✓ Pure business logic")
    print("  ✗ CANNOT import parent modules")
    print()
    print("USAGE FROM MODULES:")
    print("  from ai_mail.apps.handlers.email.footer import append_footer")
    print("  from ai_mail.apps.handlers.email.footer import get_footer")
    print()
    print("="*70 + "\n")
