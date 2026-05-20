from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import Settings, get_settings
from app.models import HealthResponse, SearchRequest, SearchResponse
from app.rate_limit import SlidingWindowLimiter
from app.search_adapter.common import probe_vertex
from app.search_service import run_search_cached

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    cfg = get_settings()
    app.state.rate_limiter = SlidingWindowLimiter(
        max_calls=cfg.rate_limit_requests_per_minute,
        window_seconds=60,
    )
    yield


app = FastAPI(
    title="QuickPickr Query Service",
    version="0.2.0",
    description="Search quick-commerce prices via Vertex AI Search",
    lifespan=lifespan,
)

_settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _settings_dep() -> Settings:
    return get_settings()




@app.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(_settings_dep)) -> HealthResponse:
    creds_set = bool(settings.google_application_credentials)
    serving = bool(settings.vertex_search_serving_config)
    if not serving:
        return HealthResponse(
            status="error",
            vertexConfigured=False,
            credentialsPathSet=creds_set,
            message="Set VERTEX_SEARCH_SERVING_CONFIG in .env",
        )
    try:
        probe_vertex(settings)
        return HealthResponse(
            status="ok",
            vertexConfigured=True,
            credentialsPathSet=creds_set,
            servingConfig=settings.vertex_search_serving_config,
            message="Vertex AI Search reachable",
        )
    except Exception as exc:  # noqa: BLE001
        return HealthResponse(
            status="degraded",
            vertexConfigured=True,
            credentialsPathSet=creds_set,
            servingConfig=settings.vertex_search_serving_config,
            message=str(exc),
        )


@app.post("/v1/search", response_model=SearchResponse)
async def search(
    body: SearchRequest,
    x_session_id: str | None = Header(default=None, alias="X-Session-Id"),
    settings: Settings = Depends(_settings_dep),
) -> SearchResponse:
    session_id = (x_session_id or "").strip() or "anonymous-session"
    if settings.enable_rate_limit:
        limiter: SlidingWindowLimiter = app.state.rate_limiter
        limiter.check(session_id)
    return await run_search_cached(body, settings)


@app.get("/")
def dev_search_page() -> FileResponse:
    """Minimal web UI for local Vertex search testing."""
    index = STATIC_DIR / "index.html"
    if not index.exists():
        raise HTTPException(status_code=404, detail="Dev UI not found")
    return FileResponse(index)
