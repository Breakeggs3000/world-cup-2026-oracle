"""Tests for WC 2026 fixtures API probabilities."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.data import store  # noqa: E402
from app.data.loader import clear_wc2026_cache  # noqa: E402
from app.main import app  # noqa: E402


class _FakePredictor:
    def predict_match(self, home, away, match_date, history_df, **kwargs):
        return {
            "probabilities": {"W": 0.45, "D": 0.25, "L": 0.30},
            "predicted_outcome": "W",
            "elo_home": 1520.0,
            "elo_away": 1480.0,
        }

    def implied_scoreline(self, probs, elo_home, elo_away):
        return "2-1"

    def top_outcomes(self, probs, elo_home, elo_away, n=5):
        return [
            {"score": "2-1", "probability": 0.11},
            {"score": "1-1", "probability": 0.10},
            {"score": "1-0", "probability": 0.09},
            {"score": "2-0", "probability": 0.08},
            {"score": "0-1", "probability": 0.07},
        ]


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def seeded_db(tmp_path: Path, monkeypatch):
    db = str(tmp_path / "fixtures.db")
    monkeypatch.setenv("FIXTURES_DB_PATH", db)
    monkeypatch.setattr(store, "DEFAULT_DB_PATH", db)
    clear_wc2026_cache()
    store.upsert_fixtures(
        [
            {
                "id": 1,
                "date": "2026-06-11",
                "datetime": "2026-06-11T13:00:00Z",
                "home_team": "Mexico",
                "away_team": "South Africa",
                "stage": "group",
                "group": "A",
                "status": "played",
                "home_score": 2,
                "away_score": 0,
            },
            {
                "id": 2,
                "date": "2026-06-13",
                "datetime": "2026-06-13T21:00:00Z",
                "home_team": "Haiti",
                "away_team": "Scotland",
                "stage": "group",
                "group": "C",
                "status": "upcoming",
            },
        ],
        db_path=db,
    )
    clear_wc2026_cache()
    return db


@pytest.fixture()
def mock_predictor(monkeypatch):
    fake = _FakePredictor()
    fake_df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01"]),
            "home_team": ["Brazil"],
            "away_team": ["Argentina"],
            "home_score": [1],
            "away_score": [0],
            "tournament": ["Friendly"],
            "city": [""],
            "country": [""],
        }
    )
    monkeypatch.setattr(
        "app.api.wc2026.get_trained_system",
        lambda: (fake, fake_df, fake_df),
    )


def test_wc2026_fixtures_include_probabilities(client, seeded_db, mock_predictor):
    res = client.get("/api/v1/wc2026/fixtures?status=all&sort=datetime&order=asc")
    assert res.status_code == 200
    body = res.json()
    assert body["count"] == 2

    played = body["fixtures"][0]
    assert played["stage"] == "Group"
    assert played["probabilities"] == {"W": 0.45, "D": 0.25, "L": 0.30}
    assert played["predicted_outcome"] == "W"
    assert played["likely_scoreline"] == "2-1"
    assert len(played["top_outcomes"]) == 5
    assert played["top_outcomes"][0]["score"] == "2-1"

    upcoming = body["fixtures"][1]
    assert upcoming["probabilities"]["W"] == 0.45
    assert len(upcoming["top_outcomes"]) == 5


def test_store_normalizes_lowercase_group_stage(tmp_path: Path):
    db = str(tmp_path / "norm.db")
    store.upsert_fixtures(
        [
            {
                "id": 1,
                "date": "2026-06-11",
                "datetime": "2026-06-11T13:00:00Z",
                "home_team": "Mexico",
                "away_team": "South Africa",
                "stage": "group",
                "group": "A",
                "status": "upcoming",
            }
        ],
        db_path=db,
    )
    rows = store.query_fixtures(db_path=db)
    assert rows[0]["stage"] == "Group"
