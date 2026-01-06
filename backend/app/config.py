import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()