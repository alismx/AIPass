"""
PRAX Modules - Public API

Modules in this directory are SERVICES that PRAX provides to other branches.
Other branches import from here to use PRAX services.

Available modules:
- logger: System-wide logging service
  Import: from aipass.prax.apps.modules.logger import system_logger

  Usage:
    system_logger.info("Your message")
    system_logger.warning("Warning message")
    system_logger.error("Error message")

  Logs auto-route to: {repo_root}/system_logs/<your_module>.log
"""
