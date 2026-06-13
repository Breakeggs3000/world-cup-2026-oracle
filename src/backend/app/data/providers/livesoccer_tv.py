"""LiveSoccerTV HTML fallback (deprecated — use duckduckgo_search instead)."""

from __future__ import annotations

import os
from typing import Any

import httpx

from app.data import store
from app.data.providers.score_html import apply_score_updates, parse_score_updates

URL = "https://www.livesoccertv.com/competitions/world-cup/"


class LiveSoccerTvProvider:
    name = "livesoccer_tv"

    def __init__(self, enabled: bool | None = None, db_path: str | None = None):
        flag = os.environ.get("LIVESOCCERTV_FALLBACK", "0")
        self.enabled = enabled if enabled is not None else flag in ("1", "true", "yes")
        self.db_path = db_path

    def fetch_fixtures(self) -> list[dict[str, Any]]:
        if not self.enabled:
            raise RuntimeError("LiveSoccerTV fallback disabled")

        existing = store.query_fixtures(db_path=self.db_path)
        if not existing:
            raise RuntimeError("No fixtures in DB to update from LiveSoccerTV")

        with httpx.Client(
            timeout=30.0,
            headers={"User-Agent": "WorldCup2026Oracle/1.1 (+informational; sync fallback)"},
            follow_redirects=True,
        ) as client:
            response = client.get(URL)
            response.raise_for_status()
            html = response.text

        updates = parse_score_updates(html)
        if not updates:
            raise RuntimeError("No scores parsed from LiveSoccerTV")

        return apply_score_updates(existing, updates)
