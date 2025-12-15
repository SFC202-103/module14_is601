# app/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "FastAPI Calculator"
    APP_VERSION: str = "1.0.0"
    BASE_URL: str = "http://localhost:8000"
    
    # Database settings (keeping your existing default)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/fastapi_db"
    TEST_DATABASE_URL: Optional[str] = "postgresql://postgres:postgres@localhost:5432/fastapi_test_db"
    
    # JWT Settings
    JWT_SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    JWT_REFRESH_SECRET_KEY: str = "your-refresh-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Email verification settings
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_EXPIRE_MINUTES: int = 60
    
    # Security
    BCRYPT_ROUNDS: int = 12
    CORS_ORIGINS: List[str] = ["*"]
    
    # Redis (optional, for token blacklisting)
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    
    # Email/SMTP Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "noreply@example.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create a global settings instance
settings = Settings()

# Optional: Add cached settings getter
@lru_cache()
def get_settings() -> Settings:
    return Settings()