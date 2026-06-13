"""Walk-forward backtesting and metrics for match outcome predictions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from app.data.loader import get_world_cup_matches, is_world_cup_row, load_results, outcome_label
from app.model.elo import EloEngine
from app.model.predictor import OUTCOME_ORDER, MatchPredictor

TRAIN_END = pd.Timestamp("2017-12-31")
VAL_END = pd.Timestamp("2022-12-31")


def ranked_probability_score(probs: dict[str, float], actual: str) -> float:
    cum = 0.0
    for cls in OUTCOME_ORDER:
        cum += probs[cls]
        if cls == actual:
            return cum - probs[actual]
    return 1.0


def brier_score_multiclass(probs: dict[str, float], actual: str) -> float:
    return sum((probs[c] - (1.0 if c == actual else 0.0)) ** 2 for c in OUTCOME_ORDER) / len(
        OUTCOME_ORDER
    )


def log_loss(probs: dict[str, float], actual: str, eps: float = 1e-15) -> float:
    p = max(eps, min(1 - eps, probs.get(actual, eps)))
    return -float(np.log(p))


def calibration_bins(predictions: list[dict[str, Any]], n_bins: int = 10) -> list[dict[str, float]]:
    bins: list[list[dict[str, Any]]] = [[] for _ in range(n_bins)]
    for pred in predictions:
        max_prob = max(pred["probabilities"].values())
        idx = min(n_bins - 1, int(max_prob * n_bins))
        bins[idx].append(pred)

    result = []
    for i, bucket in enumerate(bins):
        if not bucket:
            continue
        avg_conf = np.mean([max(p["probabilities"].values()) for p in bucket])
        accuracy = np.mean([p["correct"] for p in bucket])
        result.append(
            {
                "bin": i + 1,
                "count": len(bucket),
                "avg_confidence": round(float(avg_conf), 4),
                "accuracy": round(float(accuracy), 4),
            }
        )
    return result


def naive_baseline_prediction(elo_home: float, elo_away: float) -> str:
    if abs(elo_home - elo_away) < 30:
        return "D"
    return "W" if elo_home > elo_away else "L"


def build_training_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, MatchPredictor]:
    engine = EloEngine()
    predictor = MatchPredictor(elo_engine=engine)

    rows: list[dict[str, Any]] = []
    for _, row in df.sort_values("date").iterrows():
        elo_home_pre = engine.get_rating(str(row["home_team"]))
        elo_away_pre = engine.get_rating(str(row["away_team"]))
        history = df[df["date"] < row["date"]]
        features = predictor.build_features_for_row(row, history, elo_home_pre, elo_away_pre)
        actual = outcome_label(int(row["home_score"]), int(row["away_score"]))
        rows.append(
            {
                "date": row["date"],
                "home_team": row["home_team"],
                "away_team": row["away_team"],
                "tournament": row.get("tournament", ""),
                "features": features,
                "outcome": actual,
                "elo_home_pre": elo_home_pre,
                "elo_away_pre": elo_away_pre,
            }
        )
        engine.process_match(row)

    enriched = pd.DataFrame(rows)
    enriched["is_knockout"] = enriched["tournament"].map(
        lambda t: any(k in str(t).lower() for k in ("final", "semi", "quarter", "round of"))
    )
    return enriched, predictor


def evaluate_predictions(predictions: list[dict[str, Any]]) -> dict[str, Any]:
    if not predictions:
        return {"accuracy": 0.0, "log_loss": 0.0, "brier": 0.0, "rps": 0.0, "count": 0}

    correct = [p["correct"] for p in predictions]
    return {
        "accuracy": round(float(np.mean(correct)), 4),
        "log_loss": round(float(np.mean([p["log_loss"] for p in predictions])), 4),
        "brier": round(float(np.mean([p["brier"] for p in predictions])), 4),
        "rps": round(float(np.mean([p["rps"] for p in predictions])), 4),
        "count": len(predictions),
    }


def predict_split(
    enriched: pd.DataFrame,
    predictor: MatchPredictor,
    mask: pd.Series,
) -> list[dict[str, Any]]:
    subset = enriched[mask]
    x = np.vstack(subset["features"].values)
    outcomes = subset["outcome"].tolist()
    probs_list = [predictor.predict_proba_vector(xi) for xi in x]

    predictions: list[dict[str, Any]] = []
    for (_, row), probs, actual in zip(subset.iterrows(), probs_list, outcomes):
        predicted = max(probs, key=probs.get)
        naive = naive_baseline_prediction(row["elo_home_pre"], row["elo_away_pre"])
        predictions.append(
            {
                "date": row["date"].strftime("%Y-%m-%d"),
                "home_team": row["home_team"],
                "away_team": row["away_team"],
                "tournament": row["tournament"],
                "probabilities": {k: round(v, 4) for k, v in probs.items()},
                "predicted": predicted,
                "actual": actual,
                "correct": predicted == actual,
                "naive_correct": naive == actual,
                "log_loss": log_loss(probs, actual),
                "brier": brier_score_multiclass(probs, actual),
                "rps": ranked_probability_score(probs, actual),
            }
        )
    return predictions


def run_backtest(output_path: Path | None = None) -> dict[str, Any]:
    df = load_results()
    enriched, predictor = build_training_dataset(df)

    train_mask = enriched["date"] <= TRAIN_END
    val_mask = (enriched["date"] > TRAIN_END) & (enriched["date"] <= VAL_END)
    test_mask = enriched["date"] > VAL_END

    x_train = np.vstack(enriched.loc[train_mask, "features"].values)
    y_train = enriched.loc[train_mask, "outcome"].tolist()
    predictor.fit(x_train, y_train)

    return _evaluate_fitted_model(enriched, predictor, val_mask, test_mask, output_path)


def _evaluate_fitted_model(
    enriched: pd.DataFrame,
    predictor: MatchPredictor,
    val_mask: pd.Series,
    test_mask: pd.Series,
    output_path: Path | None = None,
) -> dict[str, Any]:
    val_preds = predict_split(enriched, predictor, val_mask)
    test_preds = predict_split(enriched, predictor, test_mask)

    wc_years = sorted(get_world_cup_matches()["wc_year"].unique())
    wc_results: dict[str, Any] = {}
    for year in wc_years:
        if year < 1990:
            continue
        year_mask = enriched["tournament"].map(is_world_cup_row) & (
            enriched["date"].dt.year == year
        )
        wc_preds = predict_split(enriched, predictor, year_mask)
        wc_results[str(year)] = evaluate_predictions(wc_preds)

    val_metrics = evaluate_predictions(val_preds)
    test_metrics = evaluate_predictions(test_preds)
    naive_test = float(np.mean([p["naive_correct"] for p in test_preds])) if test_preds else 0.0

    report = {
        "splits": {
            "train": f"<= {TRAIN_END.date()}",
            "validation": f"{TRAIN_END.date()} – {VAL_END.date()}",
            "test": f"> {VAL_END.date()}",
        },
        "validation": val_metrics,
        "test": test_metrics,
        "naive_baseline_test_accuracy": round(naive_test, 4),
        "beats_naive_by": round(test_metrics["accuracy"] - naive_test, 4),
        "calibration": calibration_bins(test_preds),
        "world_cups": wc_results,
        "confusion_matrix": _confusion_matrix(test_preds),
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report


def _confusion_matrix(predictions: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    matrix = {a: {p: 0 for p in OUTCOME_ORDER} for a in OUTCOME_ORDER}
    for pred in predictions:
        matrix[pred["actual"]][pred["predicted"]] += 1
    return matrix
