"""
User Handlers - User Configuration and Management

Handles loading of user configuration files and user information for AI_Mail system.
"""

from .load import (
    load_user_config,
    load_config,
    create_default_config,
    load_or_create_config
)

from .user import (
    get_current_user,
    get_user_by_email,
    get_all_users
)

__all__ = [
    # Config loading
    'load_user_config',
    'load_config',
    'create_default_config',
    'load_or_create_config',

    # User info
    'get_current_user',
    'get_user_by_email',
    'get_all_users',
]
