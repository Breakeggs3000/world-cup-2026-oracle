"""Live fixture sync orchestration."""

from __future__ import annotations

import os
from typing import Any

from app.data import store
from app.data.loader import WC2026_PATH, clear_wc2026_cache
from app.data.providers.api_football import ApiFootballProvider
from app.data.providers.base import run_provider_chain
from app.data.providers.livesoccer_tv import LiveSoccerTvProvider


def build_providers(*, allow_fallback: bool = True) -> list:
    providers: list = [ApiFootballProvider()]
    if allow_fallback and os.environ.get("LIVESOCCERTV_FALLBACK", "0") in ("1", "true", "yes"):
        providers.append(LiveSoccerTvProvider())
    return providers


def run_sync(*, seed_only: bool = False) -> dict[str, Any]:
    db_path = store.DEFAULT_DB_PATH
    store.init_db(db_path)

    if seed_only or store.fixture_count(db_path) == 0:
        count = store.seed_from_json(WC2026_PATH, db_path=db_path)
        store.record_sync_run("seed", "ok", rows_updated=count, db_path=db_path)
        clear_wc2026_cache()
        return {"provider": "seed", "rows_updated": count, "status": "ok"}

    try:
        fixtures, provider = run_provider_chain(build_providers())
        count = store.upsert_fixtures(fixtures, db_path=db_path)
        store.record_sync_run(provider, "ok", rows_updated=count, db_path=db_path)
        clear_wc2026_cache()
        return {"provider": provider, "rows_updated": count, "status": "ok"}
    except Exception as exc:
        store.record_sync_run("error", "failed", error=str(exc), db_path=db_path)
        clear_wc2026_cache()
        return {"provider": "error", "rows_updated": 0, "status": "failed", "error": str(exc)}


def sync_status() -> dict[str, Any]:
    last = store.last_sync_status()
    count = store.fixture_count()
    return {
        "fixture_count": count,
        "last_sync": last,
        "data_source": last["provider"] if last and last.get("status") == "ok" else "seed",
    }
