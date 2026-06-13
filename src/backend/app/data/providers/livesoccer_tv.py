"""LiveSoccerTV HTML fallback — updates scores on known fixtures only."""

from __future__ import annotations

import os
import re
from typing import Any

import httpx

from app.data import store
from app.data.loader import normalize_team

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

        score_pattern = re.compile(
            r"(\w[\w\s\.]+?)\s+(\d+)\s*[-–]\s*(\d+)\s+(\w[\w\s\.]+)",
            re.IGNORECASE,
        )
        updates: dict[tuple[str, str], tuple[int, int]] = {}
        for match in score_pattern.finditer(html):
            home = normalize_team(match.group(1).strip())
            away = normalize_team(match.group(4).strip())
            if home and away:
                updates[(home, away)] = (int(match.group(2)), int(match.group(3)))

        if not updates:
            raise RuntimeError("No scores parsed from LiveSoccerTV")

        updated: list[dict[str, Any]] = []
        for fx in existing:
            item = dict(fx)
            key = (fx["home_team"], fx["away_team"])
            rev = (fx["away_team"], fx["home_team"])
            if key in updates:
                hs, aws = updates[key]
            elif rev in updates:
                aws, hs = updates[rev]
            else:
                updated.append(item)
                continue
            item["home_score"] = hs
            item["away_score"] = aws
            item["status"] = "played"
            updated.append(item)
        return updated
