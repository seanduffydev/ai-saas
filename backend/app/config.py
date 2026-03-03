"""Application configuration and environment settings."""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        supabase_url: Supabase project URL for database and auth.
        supabase_key: Supabase anon/service key for API access.
        openai_api_key: OpenAI API key for optional AI features.
        news_api_key: Legacy news API key (if used).
        alpha_vantage_api_key: Alpha Vantage API key for market news.
    """

    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    news_api_key: str = os.getenv("NEWS_API_KEY", "")
    alpha_vantage_api_key: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")

    class Config:
        """Pydantic config for loading from .env with case-insensitive keys."""

        env_file = ".env"
        case_sensitive = False


settings = Settings()
