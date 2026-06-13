"""Tests for SQLite fixture store."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.data import store


@pytest.fixture()
def db_path(tmp_path: Path) -> str:
    return str(tmp_path / "test.db")


def test_seed_and_sort_asc(db_path: str):
    fixtures = [
        {"id": 2, "date": "2026-06-12", "datetime": "2026-06-12T18:00:00Z", "home_team": "B", "away_team": "C", "stage": "Group", "group": "A", "status": "upcoming"},
        {"id": 1, "date": "2026-06-11", "datetime": "2026-06-11T13:00:00Z", "home_team": "A", "away_team": "B", "stage": "Group", "group": "A", "status": "upcoming"},
    ]
    store.upsert_fixtures(fixtures, db_path=db_path)
    rows = store.query_fixtures(sort="datetime", order="asc", db_path=db_path)
    assert rows[0]["id"] == 1
    assert rows[1]["id"] == 2


def test_filter_status(db_path: str):
    fixtures = [
        {"id": 1, "date": "2026-06-11", "datetime": "2026-06-11T13:00:00Z", "home_team": "A", "away_team": "B", "stage": "Group", "group": "A", "status": "played", "home_score": 1, "away_score": 0},
        {"id": 2, "date": "2026-06-12", "datetime": "2026-06-12T18:00:00Z", "home_team": "C", "away_team": "D", "stage": "Group", "group": "B", "status": "upcoming"},
    ]
    store.upsert_fixtures(fixtures, db_path=db_path)
    played = store.query_fixtures(status="played", db_path=db_path)
    assert len(played) == 1
    assert played[0]["home_score"] == 1
