# app/core/config.py
from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # --- App ---
    APP_NAME: str = "Dezh"
    APP_ENV: Literal["dev", "staging", "prod"] = "dev"
    DEBUG: bool = False
    SECRET_KEY: str = Field(default="change-me-in-production")
    API_PREFIX: str = "/api/v1"

    # --- Database (Laravel-style) ---
    DB_CONNECTION: Literal["sqlite", "pgsql", "mysql"] = "sqlite"

    # sqlite
    DB_DATABASE: str = "storage/db/dezh.db"

    # pgsql / mysql
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    DB_DATABASE_NAME: str = "dezh"
    DB_USERNAME: str = "dezh"
    DB_PASSWORD: str = ""

    # --- Security ---
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_ALGORITHM: str = "HS256"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # --- AI ---
    OPENAI_API_KEY: str | None = None
    OPENAI_BASE_URL: str = "https://api.deepseek.com/v1"
    OPENAI_MODEL: str = "deepseek-chat"

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.APP_ENV == "prod":
            if self.DEBUG:
                raise ValueError("DEBUG must be false in production")
            if self.SECRET_KEY == "change-me-in-production":
                raise ValueError("SECRET_KEY must be changed in production")
        return self

    @property
    def database_url(self) -> str:
        """SQLAlchemy async URL based on DB_CONNECTION."""
        conn = self.DB_CONNECTION

        if conn == "sqlite":
            return f"sqlite+aiosqlite:///{self.DB_DATABASE}"

        if conn == "pgsql":
            return (
                f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE_NAME}"
            )

        if conn == "mysql":
            return (
                f"mysql+aiomysql://{self.DB_USERNAME}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE_NAME}"
            )

        raise ValueError(f"Unsupported DB_CONNECTION: {conn}")

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()