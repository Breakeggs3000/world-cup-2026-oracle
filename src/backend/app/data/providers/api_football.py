"""API-Football (api-sports.io) fixture provider."""

from __future__ import annotations

import os
from typing import Any

import httpx

from app.data.loader import normalize_team

BASE_URL = "https://v3.football.api-sports.io"
DEFAULT_LEAGUE_ID = os.environ.get("API_FOOTBALL_LEAGUE_ID", "1")
DEFAULT_SEASON = os.environ.get("API_FOOTBALL_SEASON", "2026")


class ApiFootballProvider:
    name = "api_football"

    def __init__(self, api_key: str | None = None, league_id: str | None = None, season: str | None = None):
        self.api_key = api_key or os.environ.get("API_FOOTBALL_KEY", "")
        self.league_id = league_id or DEFAULT_LEAGUE_ID
        self.season = season or DEFAULT_SEASON

    def fetch_fixtures(self) -> list[dict[str, Any]]:
        if not self.api_key:
            raise RuntimeError("API_FOOTBALL_KEY not set")

        headers = {"x-apisports-key": self.api_key}
        params = {"league": self.league_id, "season": self.season}
        with httpx.Client(timeout=60.0) as client:
            response = client.get(f"{BASE_URL}/fixtures", headers=headers, params=params)
            response.raise_for_status()
            payload = response.json()
            if payload.get("errors"):
                raise RuntimeError(str(payload["errors"]))
            raw = payload.get("response") or []

        fixtures: list[dict[str, Any]] = []
        for idx, item in enumerate(raw, start=1):
            fx = item.get("fixture", {})
            teams = item.get("teams", {})
            goals = item.get("goals", {})
            league = item.get("league", {})
            home = normalize_team(teams.get("home", {}).get("name"))
            away = normalize_team(teams.get("away", {}).get("name"))
            if not home or not away:
                continue
            status_short = fx.get("status", {}).get("short", "NS")
            played = status_short in ("FT", "AET", "PEN")
            home_score = goals.get("home")
            away_score = goals.get("away")
            fixtures.append(
                {
                    "id": fx.get("id") or idx,
                    "external_id": str(fx.get("id", "")),
                    "date": (fx.get("date") or "")[:10],
                    "datetime": fx.get("date"),
                    "home_team": home,
                    "away_team": away,
                    "stage": "Group" if "Group" in str(league.get("round", "")) else league.get("round", "Group"),
                    "group": _extract_group(league.get("round", "")),
                    "venue": fx.get("venue", {}).get("name", ""),
                    "neutral": True,
                    "home_score": home_score if played else None,
                    "away_score": away_score if played else None,
                    "status": "played" if played else "upcoming",
                }
            )
        return fixtures


def _extract_group(round_name: str) -> str:
    text = str(round_name)
    for letter in "ABCDEFGHIJKL":
        if f"Group {letter}" in text or f"Group - {letter}" in text:
            return letter
    return ""
