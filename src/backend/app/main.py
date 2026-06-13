import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import create_api_router
from app.sync.scheduler import start_sync_scheduler, stop_sync_scheduler
from app.sync.service import run_sync
from app.version import API_VERSION

logger = logging.getLogger("uvicorn.error")

_DEFAULT_ORIGINS = ("http://localhost:5173", "http://127.0.0.1:5173")


def _allowed_origins() -> list[str]:
    origins = list(_DEFAULT_ORIGINS)
    extra = os.environ.get("ALLOWED_ORIGINS", "")
    for origin in extra.split(","):
        cleaned = origin.strip()
        if cleaned and cleaned not in origins:
            origins.append(cleaned)
    return origins


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start accepting requests immediately; model loads lazily on first use."""
    logger.info("API v%s ready — prediction model loads on first request.", API_VERSION)
    try:
        run_sync()
    except Exception as exc:
        logger.warning("Initial fixture sync skipped: %s", exc)
    start_sync_scheduler()
    yield
    stop_sync_scheduler()


def _model_is_cached() -> bool:
    from app.services import get_trained_system

    return get_trained_system.cache_info().currsize > 0


def _health_payload() -> dict:
    from app.model.artifacts import get_active_model_id, get_active_model_version

    ready = _model_is_cached()
    payload: dict = {
        "status": "ok" if ready else "starting",
        "api_version": API_VERSION,
        "model_ready": ready,
        "active_model_id": get_active_model_id(),
        "active_model_version": get_active_model_version(),
    }
    if not ready:
        payload["message"] = "Model not loaded yet — first prediction request triggers warmup."
    return payload


app = FastAPI(title="World Cup 2026 Oracle", version=API_VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_api_router = create_api_router()
app.include_router(_api_router, prefix="/api/v1")
# Legacy unversioned paths — same handlers; prefer /api/v1 for new clients.
app.include_router(_api_router, prefix="/api")


@app.get("/api/health")
@app.get("/api/v1/health")
def health():
    return _health_payload()
