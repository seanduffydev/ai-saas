"""Database connection and client initialization."""

from supabase import create_client, Client
from app.config import settings


class Database:
    """Singleton Supabase client wrapper.

    Ensures a single shared Supabase client is used across the application.
    """

    _client: Client = None

    @classmethod
    def get_client(cls) -> Client:
        """Get or create the Supabase client instance.

        Returns:
            Supabase Client instance. Creates one on first call.
        """
        if cls._client is None:
            cls._client = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
        return cls._client


def get_supabase() -> Client:
    """Get Supabase client instance (convenience for dependency injection).

    Returns:
        Supabase Client instance.
    """
    return Database.get_client()
