from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_title: str = "Botofarm"

    api_prefix: str = Field("/api", alias="API_PREFIX")
    api_host: str = Field("0.0.0.0", alias="API_HOST")
    api_port: int = Field(8000, alias="API_PORT")

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@postgres:5432/botofarm",
        alias="DATABASE_URL",
    )

    log_level: str = Field("INFO", alias="LOG_LEVEL")


    lock_ttl_seconds: Optional[int] = Field(
        default=None,
        alias="LOCK_TTL_SECONDS",
    )

    @field_validator("lock_ttl_seconds", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    @property
    def API_PREFIX(self) -> str:
        return self.api_prefix

    @property
    def API_HOST(self) -> str:
        return self.api_host

    @property
    def API_PORT(self) -> int:
        return self.api_port


settings = Settings()
