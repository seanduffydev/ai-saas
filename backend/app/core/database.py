"""Database connection and client initialization"""

from supabase import create_client, Client
from app.config import settings


class Database:
    """Singleton Supabase client wrapper"""
    _client: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance"""
        if cls._client is None:
            cls._client = create_client(
                settings.supabase_url, 
                settings.supabase_key
            )
        return cls._client


# Convenience function for backward compatibility
def get_supabase() -> Client:
    """Get Supabase client instance"""
    return Database.get_client()
