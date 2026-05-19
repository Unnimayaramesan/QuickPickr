from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Load repo-root .env when running locally (apps/query-service -> repo root)
_REPO_ROOT = Path(__file__).resolve().parents[3]
_ENV_FILE = _REPO_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    vertex_search_serving_config: str
    google_application_credentials: str | None = None

    # Optional tuning
    vertex_page_size: int = 25
    retailer_search_timeout_ms: int = 800
    search_cache_ttl_seconds: int = 60
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


def get_settings() -> Settings:
    return Settings()
