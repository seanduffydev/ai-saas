"""Tests for security (auth)."""

import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import get_current_user, get_user_id_from_token


@pytest.mark.asyncio
async def test_get_current_user_success():
    """get_current_user returns user when supabase validates token."""
    mock_user = MagicMock()
    mock_user.id = "user-123"
    mock_user.email = "u@example.com"
    mock_supabase = MagicMock()
    mock_supabase.auth.get_user = lambda t: MagicMock(user=mock_user)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-token")
    user = await get_current_user(credentials, mock_supabase)
    assert user.id == "user-123"
    assert user.email == "u@example.com"


@pytest.mark.asyncio
async def test_get_current_user_no_user_raises_401():
    """get_current_user raises 401 when get_user returns no user."""
    mock_supabase = MagicMock()
    mock_supabase.auth.get_user = lambda t: MagicMock(user=None)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad-token")
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials, mock_supabase)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_exception_raises_401():
    """get_current_user raises 401 on exception."""
    mock_supabase = MagicMock()
    mock_supabase.auth.get_user = lambda t: (_ for _ in ()).throw(Exception("Invalid token"))
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="x")
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials, mock_supabase)
    assert exc_info.value.status_code == 401


def test_get_user_id_from_token():
    """get_user_id_from_token returns user id."""
    mock_user = MagicMock()
    mock_user.id = "uid-456"
    assert get_user_id_from_token(mock_user) == "uid-456"
