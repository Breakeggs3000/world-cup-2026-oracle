"""Parse team/score pairs from HTML or plain text snippets."""

from __future__ import annotations

import re
from typing import Any

from app.data.loader import normalize_team

# e.g. "Mexico 2-0 South Africa", "United States 4 – 1 Paraguay"
_SCORE_RE = re.compile(
    r"([A-Z][A-Za-z\s\.\'-]{0,35}?)\s+(\d{1,2})\s*[-–]\s*(\d{1,2})\s+([A-Z][A-Za-z\s\.\'-]{0,35})",
)

_TRIM_STOPS = (" in ", " at ", " on ", " vs ", " and ", " the ", " for ", " from ")


def _trim_team_name(name: str) -> str:
    text = name.strip()
    for sep in (".", ",", ";", "!", "?"):
        if sep in text:
            text = text.split(sep, 1)[0]
    lower = text.lower()
    cut = len(text)
    for stop in _TRIM_STOPS:
        idx = lower.find(stop)
        if idx > 0:
            cut = min(cut, idx)
    return text[:cut].strip(" ,.;")


def parse_score_updates(text: str) -> dict[tuple[str, str], tuple[int, int]]:
    """Extract home/away score pairs from free-form text."""
    updates: dict[tuple[str, str], tuple[int, int]] = {}
    for match in _SCORE_RE.finditer(text):
        home = normalize_team(_trim_team_name(match.group(1)))
        away = normalize_team(_trim_team_name(match.group(4)))
        if home and away:
            updates[(home, away)] = (int(match.group(2)), int(match.group(3)))
    return updates


def apply_score_updates(
    fixtures: list[dict[str, Any]],
    updates: dict[tuple[str, str], tuple[int, int]],
) -> list[dict[str, Any]]:
    """Merge parsed scores into known fixtures (home/away orientation aware)."""
    if not updates:
        return fixtures

    updated: list[dict[str, Any]] = []
    for fx in fixtures:
        item = dict(fx)
        key = (fx["home_team"], fx["away_team"])
        rev = (fx["away_team"], fx["home_team"])
        if key in updates:
            hs, aws = updates[key]
            item["home_score"] = hs
            item["away_score"] = aws
            item["status"] = "played"
        elif rev in updates:
            aws, hs = updates[rev]
            item["home_score"] = hs
            item["away_score"] = aws
            item["status"] = "played"
        updated.append(item)
    return updated
