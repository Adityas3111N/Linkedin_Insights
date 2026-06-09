import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    # Application settings
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    
    # Database connection string
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/linkedin_insights"

    # API configuration
    API_V1_STR: str = "/api/v1"

    # LinkedIn authentication credentials
    LINKEDIN_EMAIL: str = ""
    LINKEDIN_PASSWORD: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Instantiate settings to be imported across the app
settings = Settings()
