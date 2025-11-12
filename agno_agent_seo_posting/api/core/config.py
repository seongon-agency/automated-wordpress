"""
API Configuration Settings

Loads configuration from environment variables and provides
settings for the FastAPI application.
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """API Settings"""

    # API Configuration
    API_TITLE: str = "WordPress SEO Publishing API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "REST API for automated WordPress publishing with multi-project support"

    # Server Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_PREFIX: str = "/api/v1"

    # Security
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "your-secret-key-change-in-production")
    API_KEYS: List[str] = os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else []
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    # Database
    DATABASE_PATH: str = os.getenv("CLIENT_DB_PATH", "./data/clients.db")

    # CORS
    ENABLE_CORS: bool = os.getenv("ENABLE_CORS", "true").lower() == "true"

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Anthropic API (for AI features)
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Lark Suite Configuration (for future bot integration)
    LARK_APP_ID: str = os.getenv("LARK_APP_ID", "")
    LARK_APP_SECRET: str = os.getenv("LARK_APP_SECRET", "")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


# Singleton settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get settings instance"""
    return settings
