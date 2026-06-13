"""Tests for HTML score parsing and DuckDuckGo fallback provider."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.data import store  # noqa: E402
from app.data.providers.duckduckgo_search import DuckDuckGoSearchProvider  # noqa: E402
from app.data.providers.score_html import apply_score_updates, parse_score_updates  # noqa: E402


def test_parse_score_updates_from_snippet():
    html = """
    <p>Mexico 2-0 South Africa in Group A opener.</p>
    <span>United States 4 – 1 Paraguay</span>
    """
    updates = parse_score_updates(html)
    assert updates[("Mexico", "South Africa")] == (2, 0)
    assert updates[("United States", "Paraguay")] == (4, 1)


def test_apply_score_updates_merges_fixtures():
    fixtures = [
        {
            "id": 1,
            "home_team": "Mexico",
            "away_team": "South Africa",
            "status": "upcoming",
        },
        {
            "id": 2,
            "home_team": "Haiti",
            "away_team": "Scotland",
            "status": "upcoming",
        },
    ]
    updates = {("Mexico", "South Africa"): (2, 0)}
    merged = apply_score_updates(fixtures, updates)
    assert merged[0]["status"] == "played"
    assert merged[0]["home_score"] == 2
    assert merged[0]["away_score"] == 0
    assert merged[1]["status"] == "upcoming"


def test_duckduckgo_provider_updates_known_fixtures(tmp_path: Path):
    db = str(tmp_path / "ddg.db")
    store.upsert_fixtures(
        [
            {
                "id": 1,
                "date": "2026-06-11",
                "datetime": "2026-06-11T13:00:00Z",
                "home_team": "Mexico",
                "away_team": "South Africa",
                "stage": "Group",
                "group": "A",
                "status": "upcoming",
            }
        ],
        db_path=db,
    )

    fake_html = "<body>Mexico 2-0 South Africa. World Cup 2026 result</body>"
    mock_response = MagicMock()
    mock_response.text = fake_html
    mock_response.raise_for_status = MagicMock()

    provider = DuckDuckGoSearchProvider(enabled=True, db_path=db)
    with patch("app.data.providers.duckduckgo_search.httpx.Client") as client_cls:
        client = client_cls.return_value.__enter__.return_value
        client.post.return_value = mock_response
        result = provider.fetch_fixtures()

    assert result[0]["status"] == "played"
    assert result[0]["home_score"] == 2
    assert result[0]["away_score"] == 0


def test_duckduckgo_provider_disabled_raises():
    provider = DuckDuckGoSearchProvider(enabled=False)
    with pytest.raises(RuntimeError, match="disabled"):
        provider.fetch_fixtures()
