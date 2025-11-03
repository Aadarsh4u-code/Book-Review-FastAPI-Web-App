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
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = ""
    JTI_EXPIRY: int = 60 * 60 # 1 hour


    model_config = SettingsConfigDict(
        env_file= os.path.join(os.getcwd(), ".env"), # absolute path to .env
        extra='ignore'
    )


# create a single instance for global use
setting = Settings()

