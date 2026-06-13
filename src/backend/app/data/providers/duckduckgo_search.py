"""DuckDuckGo HTML search fallback — updates scores on known fixtures only."""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlencode

import httpx

from app.data import store
from app.data.providers.score_html import apply_score_updates, parse_score_updates

DDG_HTML_URL = "https://html.duckduckgo.com/html/"
SEARCH_QUERIES = (
    "FIFA World Cup 2026 results scores today",
    "World Cup 2026 group stage match results",
)
USER_AGENT = "WorldCup2026Oracle/1.1 (+informational; score sync fallback)"


class DuckDuckGoSearchProvider:
    name = "duckduckgo_search"

    def __init__(self, enabled: bool | None = None, db_path: str | None = None):
        flag = os.environ.get("WEB_SEARCH_FALLBACK", "0")
        self.enabled = enabled if enabled is not None else flag in ("1", "true", "yes")
        self.db_path = db_path

    def fetch_fixtures(self) -> list[dict[str, Any]]:
        if not self.enabled:
            raise RuntimeError("DuckDuckGo search fallback disabled (set WEB_SEARCH_FALLBACK=1)")

        existing = store.query_fixtures(db_path=self.db_path)
        if not existing:
            raise RuntimeError("No fixtures in DB to update from web search")

        combined_html = ""
        with httpx.Client(
            timeout=30.0,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
        ) as client:
            for query in SEARCH_QUERIES:
                response = client.post(
                    DDG_HTML_URL,
                    content=urlencode({"q": query}),
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                combined_html += response.text

        updates = parse_score_updates(combined_html)
        if not updates:
            raise RuntimeError("No scores parsed from DuckDuckGo search results")

        merged = apply_score_updates(existing, updates)
        changed = sum(
            1
            for before, after in zip(existing, merged)
            if before.get("status") != after.get("status")
            or before.get("home_score") != after.get("home_score")
        )
        if changed == 0:
            raise RuntimeError("DuckDuckGo results did not match any known fixtures")
        return merged
