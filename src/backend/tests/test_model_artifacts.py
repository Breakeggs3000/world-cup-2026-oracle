"""Tests for versioned model artifact save/load."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.model.artifacts import (  # noqa: E402
    load_model_bundle,
    model_dir,
    registry_path,
    save_model_bundle,
)
from app.model.predictor import FEATURE_NAMES, MatchPredictor


@pytest.fixture()
def temp_models_root(tmp_path, monkeypatch):
    models_root = tmp_path / "models"
    registry = models_root / "registry.json"
    monkeypatch.setattr("app.model.artifacts.MODELS_ROOT", models_root)
    monkeypatch.setattr("app.model.artifacts.REGISTRY_PATH", registry)
    monkeypatch.setattr(
        "app.model.artifacts.REPO_ROOT",
        tmp_path,
    )
    monkeypatch.setattr(
        "app.model.artifacts.compute_data_fingerprint",
        lambda csv_path=None: "test-fingerprint",
    )
    monkeypatch.setattr("app.model.artifacts.RESULTS_CSV", tmp_path / "results.csv")
    (tmp_path / "results.csv").write_text("date,home_team,away_team,home_score,away_score\n", encoding="utf-8")
    return models_root


def _tiny_bundle() -> tuple[MatchPredictor, pd.DataFrame, pd.DataFrame]:
    predictor = MatchPredictor(
        model=LogisticRegression(max_iter=200),
        scaler=StandardScaler(),
        feature_names=list(FEATURE_NAMES),
    )
    x = np.random.default_rng(0).normal(size=(12, len(FEATURE_NAMES)))
    y = ["W", "D", "L"] * 4
    predictor.fit(x, y)

    history_df = pd.DataFrame(
        {
            "date": pd.date_range("2010-01-01", periods=3, freq="ME"),
            "home_team": ["A", "B", "C"],
            "away_team": ["B", "C", "A"],
            "home_score": [1, 2, 0],
            "away_score": [0, 1, 1],
            "tournament": ["Friendly"] * 3,
            "city": [""] * 3,
            "country": [""] * 3,
        }
    )
    enriched = pd.DataFrame(
        {
            "date": pd.date_range("2018-01-01", periods=3, freq="ME"),
            "home_team": ["A", "B", "C"],
            "away_team": ["B", "C", "A"],
            "tournament": ["Friendly"] * 3,
            "outcome": ["W", "D", "L"],
            "elo_home_pre": [1500.0, 1510.0, 1490.0],
            "elo_away_pre": [1490.0, 1500.0, 1510.0],
            "features": [np.array([0.0] * len(FEATURE_NAMES), dtype=float)] * 3,
            "is_knockout": [False] * 3,
        }
    )
    return predictor, history_df, enriched


def test_save_and_load_model_bundle(temp_models_root):
    predictor, history_df, enriched = _tiny_bundle()
    metrics = {"validation": {"accuracy": 0.5}, "test": {"accuracy": 0.55}}

    out = save_model_bundle(
        model_id="test-model",
        predictor=predictor,
        history_df=history_df,
        enriched=enriched,
        metrics=metrics,
        set_active=True,
    )
    assert out == model_dir("test-model")
    assert (out / "predictor.joblib").exists()
    assert (out / "enriched.joblib").exists()

    bundle = load_model_bundle("test-model")
    assert bundle.model_id == "test-model"
    assert bundle.predictor.model is not None
    assert len(bundle.enriched) == 3

    registry = json.loads(registry_path().read_text(encoding="utf-8"))
    assert registry["active_model_id"] == "test-model"
    assert "test-model" in registry["models"]
