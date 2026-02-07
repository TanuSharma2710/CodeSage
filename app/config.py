from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Get the directory where this config.py file is located (app folder)
APP_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    database_hostname: str = Field(validation_alias="DATABASE_HOSTNAME")
    database_port: str = Field(validation_alias="DATABASE_PORT")
    database_password: str = Field(validation_alias="DATABASE_PASSWORD")
    database_name: str = Field(validation_alias="DATABASE_NAME")
    database_username: str = Field(validation_alias="DATABASE_USERNAME")
    secret_key: str = Field(validation_alias="SECRET_KEY")
    algorithm: str = Field(validation_alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(default=7, validation_alias="REFRESH_TOKEN_EXPIRE_DAYS")
    groq_api_key: str = Field(default="", validation_alias="GROQ_API_KEY")

    model_config = SettingsConfigDict(
        env_file=(APP_DIR / ".env", APP_DIR.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()

