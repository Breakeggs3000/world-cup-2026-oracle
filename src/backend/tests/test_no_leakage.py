"""Tests ensuring Elo ratings have no future-data leakage."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.data.loader import load_results  # noqa: E402
from app.model.elo import EloEngine  # noqa: E402


@pytest.fixture(scope="module")
def results_df():
    try:
        return load_results()
    except FileNotFoundError:
        pytest.skip("results.csv not downloaded; run scripts/fetch_data.py")


def test_no_leakage_mid_2018(results_df: pd.DataFrame):
    cutoff = pd.Timestamp("2018-06-15")
    truncated = results_df[results_df["date"] <= cutoff]
    full_prefix = results_df[results_df["date"] <= cutoff]

    engine_trunc = EloEngine()
    engine_trunc.process_dataframe(truncated)

    engine_full = EloEngine()
    engine_full.process_dataframe(full_prefix)

    common_teams = set(engine_trunc.ratings) & set(engine_full.ratings)
    assert common_teams, "Expected overlapping teams in both runs"

    for team in common_teams:
        assert engine_trunc.ratings[team] == pytest.approx(engine_full.ratings[team], rel=1e-9)
