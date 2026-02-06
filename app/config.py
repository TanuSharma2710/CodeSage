from pydantic_settings import BaseSettings
from pathlib import Path

# Get the directory where this config.py file is located (app folder)
APP_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int = 7  # Refresh token expires in 7 days
    groq_api_key: str = ""

    class Config:
        env_file = APP_DIR / ".env"


settings = Settings()

