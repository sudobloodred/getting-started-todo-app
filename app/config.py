"""Application configuration and shared settings."""

import os
from functools import lru_cache
from typing import List

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    environment: str = Field(default="development", env="APP_ENV")
    secret_key: str = Field("", description="A strong APP_SECRET_KEY is required in production.", env="APP_SECRET_KEY")
    access_token_expiry_minutes: int = Field(
        60, description="Minutes until an issued access token expires."
    )
    allow_origins: List[str] = Field(
        default_factory=list,
        description="Origins allowed by CORS middleware.",
        env="APP_ALLOW_ORIGINS",
    )

    def validate_runtime(self) -> None:
        if self.environment.lower() == "production":
            if len(self.secret_key) < 32:
                raise RuntimeError("APP_SECRET_KEY must be at least 32 characters in production")
            if not self.allow_origins or "*" in self.allow_origins:
                raise RuntimeError("APP_ALLOW_ORIGINS must contain explicit origins in production")

    class Config:
        env_file = ".env"

        @classmethod
        def parse_env_var(cls, field_name: str, raw_value: str):  # type: ignore[override]
            if field_name == "allow_origins":
                return [origin.strip() for origin in raw_value.split(",") if origin.strip()]
            return raw_value


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance to avoid repeated parsing."""

    return Settings()
