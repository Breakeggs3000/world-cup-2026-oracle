"""Persist trained models and a registry for multi-model workflows (CV, ensembles, RL)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from app.data.loader import RESULTS_CSV
from app.model.backtest import TRAIN_END, VAL_END, build_training_dataset, _evaluate_fitted_model
from app.model.elo import EloEngine
from app.model.predictor import FEATURE_NAMES, MatchPredictor
from app.version import DEFAULT_MODEL_VERSION

REPO_ROOT = Path(__file__).resolve().parents[4]
MODELS_ROOT = REPO_ROOT / "workspace" / "artifacts" / "models"
REGISTRY_PATH = MODELS_ROOT / "registry.json"
DEFAULT_MODEL_ID = "elo-logistic-v1"


@dataclass
class ModelBundle:
    """Loaded model artifact set ready for inference or evaluation."""

    model_id: str
    metadata: dict[str, Any]
    predictor: MatchPredictor
    history_df: pd.DataFrame
    enriched: pd.DataFrame
    elo_ratings: dict[str, float]


def models_root() -> Path:
    return MODELS_ROOT


def registry_path() -> Path:
    return REGISTRY_PATH


def model_dir(model_id: str) -> Path:
    return MODELS_ROOT / model_id


def compute_data_fingerprint(csv_path: Path | None = None) -> str:
    path = csv_path or RESULTS_CSV
    if not path.exists():
        return "missing"
    stat = path.stat()
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    # Content + size only — mtime changes whenever CSV is re-downloaded on deploy.
    return f"sha256:{digest.hexdigest()}:{stat.st_size}"


def _normalize_data_fingerprint(fingerprint: str) -> str:
    """Compare fingerprints ignoring legacy mtime suffix."""
    parts = fingerprint.split(":")
    if len(parts) >= 3 and parts[0] == "sha256":
        return ":".join(parts[:3])
    return fingerprint


def artifacts_match_committed_data(model_id: str | None = None) -> bool:
    """Lightweight check — no joblib load. Used during Docker build."""
    resolved_id = model_id or get_active_model_id()
    if not resolved_id or not model_bundle_exists(resolved_id):
        return False
    metadata_path = model_dir(resolved_id) / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    expected = _normalize_data_fingerprint(metadata.get("data_fingerprint", ""))
    current = _normalize_data_fingerprint(compute_data_fingerprint())
    return bool(expected) and expected == current


def list_models() -> list[dict[str, Any]]:
    registry = load_registry()
    return list(registry.get("models", {}).values())


def get_active_model_id() -> str | None:
    registry = load_registry()
    return registry.get("active_model_id")


def get_active_model_version() -> str | None:
    registry = load_registry()
    if registry.get("active_model_version"):
        return registry["active_model_version"]
    model_id = registry.get("active_model_id")
    if not model_id:
        return None
    entry = registry.get("models", {}).get(model_id, {})
    return entry.get("model_version")


def load_registry() -> dict[str, Any]:
    if not REGISTRY_PATH.exists():
        return {
            "schema_version": 1,
            "api_version": "1.0.0",
            "active_model_id": None,
            "active_model_version": None,
            "models": {},
        }
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    # Migrate legacy registry shape.
    if "schema_version" not in registry and "version" in registry:
        registry["schema_version"] = registry.pop("version")
    return registry


def save_registry(registry: dict[str, Any]) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding="utf-8")


def model_bundle_exists(model_id: str) -> bool:
    root = model_dir(model_id)
    return (root / "metadata.json").exists() and (root / "predictor.joblib").exists()


def save_model_bundle(
    *,
    model_id: str,
    predictor: MatchPredictor,
    history_df: pd.DataFrame,
    enriched: pd.DataFrame,
    metrics: dict[str, Any],
    name: str | None = None,
    family: str = "elo_logistic",
    algorithm: str = "LogisticRegression",
    tags: list[str] | None = None,
    hyperparameters: dict[str, Any] | None = None,
    set_active: bool = False,
    notes: str = "",
    model_version: str | None = None,
) -> Path:
    """Write predictor, enriched features, Elo snapshot, metrics, and registry entry."""
    out = model_dir(model_id)
    out.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        {
            "model": predictor.model,
            "scaler": predictor.scaler,
            "feature_names": predictor.feature_names,
        },
        out / "predictor.joblib",
    )

    joblib.dump(enriched, out / "enriched.joblib")

    elo_engine = EloEngine()
    elo_engine.process_dataframe(history_df[history_df["date"] <= TRAIN_END])
    (out / "elo_ratings.json").write_text(
        json.dumps(elo_engine.snapshot_ratings(), indent=2),
        encoding="utf-8",
    )

    fingerprint = compute_data_fingerprint()
    resolved_version = model_version or DEFAULT_MODEL_VERSION
    metadata = {
        "id": model_id,
        "model_version": resolved_version,
        "name": name or model_id,
        "family": family,
        "algorithm": algorithm,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "train_end": str(TRAIN_END.date()),
        "val_end": str(VAL_END.date()),
        "feature_names": list(predictor.feature_names),
        "outcome_order": ["W", "D", "L"],
        "data_fingerprint": fingerprint,
        "data_source": str(RESULTS_CSV.relative_to(REPO_ROOT)).replace("\\", "/"),
        "tags": tags or ["baseline"],
        "hyperparameters": hyperparameters
        or {"max_iter": 1000, "random_state": 42, "classifier": "LogisticRegression"},
        "metrics": metrics,
        "notes": notes,
        "artifact_files": {
            "predictor": "predictor.joblib",
            "enriched": "enriched.joblib",
            "elo_ratings": "elo_ratings.json",
            "metrics": "metrics.json",
        },
    }
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    registry = load_registry()
    registry.setdefault("models", {})[model_id] = metadata
    registry["api_version"] = registry.get("api_version", "1.0.0")
    if set_active or registry.get("active_model_id") is None:
        registry["active_model_id"] = model_id
        registry["active_model_version"] = resolved_version
    save_registry(registry)
    return out


def load_model_bundle(model_id: str | None = None) -> ModelBundle:
    """Load a registered model bundle from disk."""
    resolved_id = model_id or get_active_model_id()
    if not resolved_id:
        raise FileNotFoundError("No active model configured in registry")

    root = model_dir(resolved_id)
    metadata_path = root / "metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Model artifact not found: {resolved_id}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload = joblib.load(root / "predictor.joblib")
    predictor = MatchPredictor(
        model=payload["model"],
        scaler=payload["scaler"],
        feature_names=payload.get("feature_names", list(FEATURE_NAMES)),
    )

    enriched = joblib.load(root / "enriched.joblib")
    elo_ratings = json.loads((root / "elo_ratings.json").read_text(encoding="utf-8"))

    from app.data.loader import load_results

    history_df = load_results()
    expected_fp = metadata.get("data_fingerprint")
    current_fp = compute_data_fingerprint()
    if expected_fp and _normalize_data_fingerprint(expected_fp) != _normalize_data_fingerprint(
        current_fp
    ):
        raise ValueError(
            f"Data fingerprint mismatch for {resolved_id}. "
            "Retrain with scripts/train_model.py after refreshing results.csv."
        )

    return ModelBundle(
        model_id=resolved_id,
        metadata=metadata,
        predictor=predictor,
        history_df=history_df,
        enriched=enriched,
        elo_ratings=elo_ratings,
    )


def train_and_save_model(
    *,
    model_id: str = DEFAULT_MODEL_ID,
    model_version: str | None = None,
    set_active: bool = True,
    tags: list[str] | None = None,
    notes: str = "",
) -> tuple[ModelBundle, dict[str, Any]]:
    """Train baseline model, run backtest metrics, and persist artifacts."""
    from app.data.loader import load_results

    df = load_results()
    enriched, predictor = build_training_dataset(df)

    train_mask = enriched["date"] <= TRAIN_END
    val_mask = (enriched["date"] > TRAIN_END) & (enriched["date"] <= VAL_END)
    test_mask = enriched["date"] > VAL_END
    x_train = np.vstack(enriched.loc[train_mask, "features"].values)
    y_train = enriched.loc[train_mask, "outcome"].tolist()
    predictor.fit(x_train, y_train)

    report_path = REPO_ROOT / "workspace" / "artifacts" / "backtest_report.json"
    report = _evaluate_fitted_model(enriched, predictor, val_mask, test_mask, report_path)
    metrics = {
        "validation": report["validation"],
        "test": report["test"],
        "beats_naive_by": report["beats_naive_by"],
        "naive_baseline_test_accuracy": report["naive_baseline_test_accuracy"],
    }

    save_model_bundle(
        model_id=model_id,
        model_version=model_version,
        predictor=predictor,
        history_df=df,
        enriched=enriched,
        metrics=metrics,
        name="Elo + Multinomial Logistic (baseline)",
        tags=tags or ["baseline", "production"],
        set_active=set_active,
        notes=notes,
    )
    return load_model_bundle(model_id), report


def try_load_active_bundle() -> ModelBundle | None:
    """Return active bundle when artifacts exist and data fingerprint matches."""
    model_id = get_active_model_id()
    if not model_id or not model_bundle_exists(model_id):
        return None
    try:
        return load_model_bundle(model_id)
    except (FileNotFoundError, ValueError):
        return None
