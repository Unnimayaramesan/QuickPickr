from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.models import HealthResponse, SearchRequest, SearchResponse
from app.search_service import run_search
from app.vertex_search import search_vertex

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="QuickPickr Query Service",
    version="0.1.0",
    description="Search quick-commerce prices via Vertex AI Search",
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
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
        # Lightweight probe: empty-ish query may still validate auth + config
        search_vertex("milk", settings, page_size=1)
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
def search(body: SearchRequest) -> SearchResponse:
    return run_search(body, settings)


@app.get("/")
def dev_search_page() -> FileResponse:
    """Minimal web UI for local Vertex search testing."""
    index = STATIC_DIR / "index.html"
    if not index.exists():
        raise HTTPException(status_code=404, detail="Dev UI not found")
    return FileResponse(index)
