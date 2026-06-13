"""Compose versioned API route groups."""

from __future__ import annotations

from fastapi import APIRouter

from app.api import backtest, matches, models, predictions, simulation, version_info, wc2026


def create_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(version_info.router)
    router.include_router(backtest.router)
    router.include_router(models.router)
    router.include_router(matches.router)
    router.include_router(predictions.router)
    router.include_router(wc2026.router)
    router.include_router(simulation.router)
    return router
