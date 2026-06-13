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
    """Pre-build the trained model so first UI request is not a multi-minute wait."""
    logger.info("Warming up prediction model (first load takes ~2–3 minutes)…")
    from app.services import get_trained_system

    get_trained_system()
    logger.info("Model ready.")
    yield


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
    from app.services import get_trained_system

    try:
        get_trained_system()
        return {
            "status": "ok",
            "model_ready": True,
            "active_model_id": get_active_model_id(),
        }
    except Exception as exc:
        return {
            "status": "degraded",
            "model_ready": False,
            "active_model_id": get_active_model_id(),
            "error": str(exc),
        }
