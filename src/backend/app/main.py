import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import backtest, matches, models, predictions, simulation, wc2026

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
    logger.info("API ready — prediction model loads on first request.")
    yield


def _model_is_cached() -> bool:
    from app.services import get_trained_system

    return get_trained_system.cache_info().currsize > 0


app = FastAPI(title="World Cup 2026 Oracle", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(backtest.router)
app.include_router(models.router)
app.include_router(matches.router)
app.include_router(predictions.router)
app.include_router(wc2026.router)
app.include_router(simulation.router)


@app.get("/api/health")
def health():
    from app.model.artifacts import get_active_model_id

    ready = _model_is_cached()
    payload: dict = {
        "status": "ok" if ready else "starting",
        "model_ready": ready,
        "active_model_id": get_active_model_id(),
    }
    if not ready:
        payload["message"] = "Model not loaded yet — first prediction request triggers warmup."
    return payload
