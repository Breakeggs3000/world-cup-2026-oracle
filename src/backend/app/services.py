"""Shared application state: trained model and cached backtest report."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from app.data.loader import load_results
from app.model.artifacts import try_load_active_bundle
from app.model.backtest import TRAIN_END, build_training_dataset, predict_split, run_backtest
from app.model.predictor import MatchPredictor

REPO_ROOT = Path(__file__).resolve().parents[3]
REPORT_PATH = REPO_ROOT / "workspace" / "artifacts" / "backtest_report.json"


@lru_cache(maxsize=1)
def get_history_df() -> pd.DataFrame:
    return load_results()


def _resolve_model_id() -> str | None:
    return os.environ.get("WC_MODEL_ID") or None


@lru_cache(maxsize=1)
def get_trained_system() -> tuple[MatchPredictor, pd.DataFrame, pd.DataFrame]:
    model_id = _resolve_model_id()
    if model_id:
        from app.model.artifacts import load_model_bundle

        bundle = load_model_bundle(model_id)
    else:
        bundle = try_load_active_bundle()
    if bundle is not None:
        return bundle.predictor, bundle.history_df, bundle.enriched

    df = get_history_df()
    enriched, predictor = build_training_dataset(df)
    train_mask = enriched["date"] <= TRAIN_END
    x_train = np.vstack(enriched.loc[train_mask, "features"].values)
    y_train = enriched.loc[train_mask, "outcome"].tolist()
    predictor.fit(x_train, y_train)
    return predictor, df, enriched


def get_backtest_report() -> dict:
    if REPORT_PATH.exists():
        return json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    return run_backtest()


def tournament_match_predictions(year: int) -> list[dict]:
    predictor, _, enriched = get_trained_system()
    mask = (enriched["date"].dt.year == year) & enriched["tournament"].str.contains(
        "FIFA World Cup", case=False, na=False
    )
    return predict_split(enriched, predictor, mask)


def list_available_models() -> dict:
    from app.model.artifacts import get_active_model_id, list_models

    return {
        "active_model_id": get_active_model_id(),
        "models": list_models(),
    }
