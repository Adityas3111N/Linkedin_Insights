from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/linkedin_insights"
    API_V1_STR: str = "/api/v1"
    LINKEDIN_EMAIL: str = ""
    LINKEDIN_PASSWORD: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
