"""Memory file management — wraps and extends trinity-pattern package.

Handles passport.json, local.json, observations.json per branch.
FIFO rollover to archive when files exceed limits.
"""
