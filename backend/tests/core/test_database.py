"""Tests for database module."""

from unittest.mock import patch, MagicMock

from app.core.database import Database, get_supabase


def test_get_supabase_returns_client():
    """get_supabase returns same client as Database.get_client."""
    with patch.object(Database, "_client", None):
        with patch("app.core.database.create_client") as mock_create:
            mock_client = MagicMock()
            mock_create.return_value = mock_client
            client1 = get_supabase()
            client2 = get_supabase()
            assert client1 is client2
            assert client1 is mock_client
            mock_create.assert_called_once()


def test_database_get_client_singleton():
    """Database.get_client returns singleton."""
    with patch.object(Database, "_client", None):
        with patch("app.core.database.create_client") as mock_create:
            mock_client = MagicMock()
            mock_create.return_value = mock_client
            c1 = Database.get_client()
            c2 = Database.get_client()
            assert c1 is c2
            mock_create.assert_called_once()
