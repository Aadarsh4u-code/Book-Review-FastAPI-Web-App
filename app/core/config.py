import os
from typing import Optional

from asyncpg.pgproto.pgproto import timedelta
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.shared.utils import EnvironmentSchema


class Settings(BaseSettings):
    APP_NAME: str = "Book Review API"
    ENVIRONMENT: str = EnvironmentSchema.DEV  # Add this

    DATABASE_URL: str = ""
    REDIS_URL: str = ""

    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRY_MIN: int = 15 # minutes
    REFRESH_TOKEN_EXPIRY_DAYS: int = 1 # days
    JWT_ISSUER: Optional[str] = None
    JWT_AUDIENCE: Optional[str] = None
    JTI_EXPIRY: int = 60 * 60  # 1 hour

    EMAIL_TOKEN_EXPIRY: int = 60 * 60 # 1 Hour


    model_config = SettingsConfigDict(
        env_file= os.path.join(os.getcwd(), ".env"), # absolute path to .env
        extra='ignore',
        case_sensitive=True
    )

    @property
    def access_token_expiry(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRY_MIN)

    @property
    def refresh_token_expiry(self) -> timedelta:
        return timedelta(days=self.REFRESH_TOKEN_EXPIRY_DAYS)



# create a single instance for global use
settings = Settings()

