import os
from pydantic_settings import BaseSettings, SettingsConfigDict





class Settings(BaseSettings):
    DATABASE_URL: str = ""
    ENVIRONMENT: str = "development"  # Add this
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRY: int = 30 # minutes
    REFRESH_TOKEN_EXPIRY: int = 1 # days
    EMAIL_TOKEN_EXPIRY: int = 60 * 60 # 1 Hour

    model_config = SettingsConfigDict(
        env_file= os.path.join(os.getcwd(), ".env"), # absolute path to .env
        extra='ignore'
    )


# create a single instance for global use
setting = Settings()

