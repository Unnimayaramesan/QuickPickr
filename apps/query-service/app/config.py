import logging
from pathlib import Path
from typing import Self

from dotenv import load_dotenv
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load repo-root .env when running locally (apps/query-service -> repo root)
_REPO_ROOT = Path(__file__).resolve().parents[3]
_ENV_FILE = _REPO_ROOT / ".env"

# Also push .env values into os.environ so Google Cloud libraries
# (which read GOOGLE_APPLICATION_CREDENTIALS from the OS environment, not
# from the pydantic Settings object) can find them.
if _ENV_FILE.exists():
    load_dotenv(_ENV_FILE)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Empty lets uvicorn boot without repo-root `.env`; Vertex stays unusable until configured.
    vertex_search_serving_config: str = ""
    google_application_credentials: str | None = None

    vertex_page_size: int = 25
    # Set true only after retailer + zoneId are filterable in the Vertex data store schema.
    # False = one unfiltered call per retailer (client-side retailer filter); much faster locally.
    vertex_use_schema_filters: bool = False  # env: VERTEX_USE_SCHEMA_FILTERS
    retailer_search_timeout_sec: float = 3.5
    # Parallel fan-out: wall clock ≈ slowest retailer; must exceed retailer_search_timeout_sec.
    total_search_budget_sec: float = 5.0
    search_cache_ttl_seconds: int = 60
    # Negative-cache TTL: applied when every retailer row is status=error.
    # Keeps a short stampede shield in front of a flapping upstream without
    # memorialising a transient failure for the full success TTL.
    # Set to 0 to skip caching all-error responses entirely.
    negative_cache_ttl_seconds: int = 5
    cors_origins: str = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:8080,http://127.0.0.1:8080"
    )

    redis_url: str | None = None
    enable_rate_limit: bool = True
    rate_limit_requests_per_minute: int = 30

    match_engine_low_threshold: float = 0.52
    match_engine_suppress_threshold: float = 0.34

    vertex_data_store_branch: str | None = None

    retailer_search_timeout_ms: int | None = None

    @model_validator(mode="after")
    def _apply_timeout_ms(self) -> Self:
        if self.retailer_search_timeout_ms is not None:
            object.__setattr__(
                self,
                "retailer_search_timeout_sec",
                max(0.05, float(self.retailer_search_timeout_ms) / 1000.0),
            )
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


_vertex_warned = False


def get_settings() -> Settings:
    global _vertex_warned
    s = Settings()
    if not (s.vertex_search_serving_config or "").strip():
        if not _vertex_warned:
            _vertex_warned = True
            logging.getLogger(__name__).warning(
                "VERTEX_SEARCH_SERVING_CONFIG is unset: copy .env.example to repo-root .env and fill "
                "Vertex fields. Search will return errors until configured.",
            )
    return s
