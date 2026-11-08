"""Application settings, loaded from environment / backend/.env.

The .env path is resolved relative to this file so the app works no matter which
directory uvicorn is launched from.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---- Database ----
    database_url: str = "postgresql+asyncpg://fifa:fifa@localhost:5544/fifa"
    database_url_sync: str = "postgresql+psycopg://fifa:fifa@localhost:5544/fifa"

    # ---- API-Football (API-SPORTS) ----
    api_football_key: str = ""
    api_football_base_url: str = "https://v3.football.api-sports.io"
    api_football_daily_budget: int = 100
    api_football_safety_reserve: int = 20

    # ---- Application ----
    frontend_url: str = "http://localhost:5173"
    environment: str = "development"
    log_level: str = "INFO"

    # Comma-separated list of extra allowed CORS origins (e.g. the deployed
    # frontend URL). Set via env CORS_ORIGINS in production.
    cors_origins_csv: str = Field(default="", alias="CORS_ORIGINS")
    # Optional regex to allow preview deploys, e.g. https://.*\.vercel\.app
    cors_origin_regex: str = Field(default="", alias="CORS_ORIGIN_REGEX")

    @property
    def cors_origins(self) -> list[str]:
        # Allow the configured frontend plus common local Vite ports.
        origins = {self.frontend_url}
        for port in (5173, 5174, 5175, 5180, 3000):
            origins.add(f"http://localhost:{port}")
            origins.add(f"http://127.0.0.1:{port}")
        for extra in self.cors_origins_csv.split(","):
            extra = extra.strip().rstrip("/")
            if extra:
                origins.add(extra)
        return sorted(origins)

    @property
    def api_football_configured(self) -> bool:
        return bool(self.api_football_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
