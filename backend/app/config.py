from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    openai_api_key: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        # Allow Railway env vars to override .env file
        case_sensitive = False

# Try to load from environment first, then .env
settings = Settings(
    supabase_url=os.getenv("SUPABASE_URL", ""),
    supabase_key=os.getenv("SUPABASE_KEY", ""),
    openai_api_key=os.getenv("OPENAI_API_KEY", "")
)