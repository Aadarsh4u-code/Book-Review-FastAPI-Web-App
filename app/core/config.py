import os
from pydantic_settings import BaseSettings, SettingsConfigDict





class Settings(BaseSettings):
    DATABASE_URL: str = ""
    ENVIRONMENT: str = "development"  # Add this

    model_config = SettingsConfigDict(
        env_file= os.path.join(os.getcwd(), ".env"), # absolute path to .env
        extra='ignore'
    )


# create a single instance for global use
setting = Settings()

