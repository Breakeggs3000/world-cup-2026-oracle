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
from app.version import API_VERSION

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
    from app.model.artifacts import get_active_model_id, get_active_model_version, list_models

    return {
        "api_version": API_VERSION,
        "active_model_id": get_active_model_id(),
        "active_model_version": get_active_model_version(),
        "models": list_models(),
    }


def get_version_info() -> dict:
    from app.model.artifacts import get_active_model_id, get_active_model_version, list_models
    from app.model.versioning import is_compatible_model_version
    from app.version import API_STATUS

    active_id = get_active_model_id()
    active_version = get_active_model_version()
    models = list_models()
    active_entry = next((m for m in models if m.get("id") == active_id), None)

    return {
        "api_version": API_VERSION,
        "api_status": API_STATUS,
        "preferred_prefix": "/api/v1",
        "legacy_prefix": "/api",
        "active_model": {
            "id": active_id,
            "version": active_version,
            "family": active_entry.get("family") if active_entry else None,
            "compatible_with_api": (
                is_compatible_model_version(API_VERSION, active_version)
                if active_version
                else None
            ),
        },
        "models": [
            {
                "id": m.get("id"),
                "model_version": m.get("model_version"),
                "family": m.get("family"),
                "name": m.get("name"),
            }
            for m in models
        ],
    }
