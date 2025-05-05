from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost/claims_db"
    
    # OpenAI settings
    OPENAI_API_KEY: str
    
    # API settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Insurance Claims Processing API"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings() 