"""Shared dependencies for API routes.

Provides injectable dependencies: get_supabase, get_current_user,
get_user_id_from_token for use in FastAPI route handlers.
"""

from fastapi import Depends
from supabase import Client

from app.core.database import get_supabase
from app.core.security import get_current_user, get_user_id_from_token

__all__ = [
    'get_supabase',
    'get_current_user',
    'get_user_id_from_token'
]
