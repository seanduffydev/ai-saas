import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    news_api_key: str = os.getenv("NEWS_API_KEY", "")
    alpha_vantage_api_key: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")  # ← Add this
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()