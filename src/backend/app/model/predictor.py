"""Elo + multinomial logistic regression match outcome predictor."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from app.data.loader import get_team_confederation, is_knockout_stage, outcome_label
from app.model.elo import EloEngine

FEATURE_NAMES = [
    "delta_elo",
    "abs_delta_elo",
    "form_5_home",
    "form_5_away",
    "form_10_home",
    "form_10_away",
    "days_rest_diff",
    "is_knockout",
    "confed_same",
    "h2h_home_win_rate",
]

OUTCOME_ORDER = ["W", "D", "L"]


@dataclass
class MatchPredictor:
    model: LogisticRegression | None = None
    scaler: StandardScaler | None = None
    elo_engine: EloEngine = field(default_factory=EloEngine)
    feature_names: list[str] = field(default_factory=lambda: list(FEATURE_NAMES))

    def _team_form(self, history: pd.DataFrame, team: str, n: int) -> float:
        rows = history[
            (history["home_team"] == team) | (history["away_team"] == team)
        ].tail(n)
        if rows.empty:
            return 1.0
        points = []
        for _, r in rows.iterrows():
            if r["home_team"] == team:
                outcome = outcome_label(int(r["home_score"]), int(r["away_score"]))
                points.append({"W": 3, "D": 1, "L": 0}[outcome])
            else:
                outcome = outcome_label(int(r["away_score"]), int(r["home_score"]))
                points.append({"W": 0, "D": 1, "L": 3}[outcome])
        return sum(points) / (3 * len(points))

    def _h2h_win_rate(self, history: pd.DataFrame, home: str, away: str) -> float:
        meetings = history[
            ((history["home_team"] == home) & (history["away_team"] == away))
            | ((history["home_team"] == away) & (history["away_team"] == home))
        ]
        if len(meetings) < 3:
            return 0.5
        wins = 0
        for _, r in meetings.iterrows():
            if r["home_team"] == home:
                if int(r["home_score"]) > int(r["away_score"]):
                    wins += 1
                elif int(r["home_score"]) == int(r["away_score"]):
                    wins += 0.5
            else:
                if int(r["away_score"]) > int(r["home_score"]):
                    wins += 1
                elif int(r["away_score"]) == int(r["home_score"]):
                    wins += 0.5
        return wins / len(meetings)

    def build_features_for_row(
        self,
        row: pd.Series,
        history: pd.DataFrame,
        elo_home: float,
        elo_away: float,
        home_adj: float = 0.0,
        away_adj: float = 0.0,
        form_boost_home: float = 0.0,
        form_boost_away: float = 0.0,
        force_knockout: bool | None = None,
    ) -> np.ndarray:
        home = str(row["home_team"])
        away = str(row["away_team"])
        prior = history[history["date"] < row["date"]]

        elo_h = elo_home + home_adj
        elo_a = elo_away + away_adj
        delta = elo_h - elo_a

        form_5_h = self._team_form(prior, home, 5) + form_boost_home
        form_5_a = self._team_form(prior, away, 5) + form_boost_away
        form_10_h = self._team_form(prior, home, 10) + form_boost_home
        form_10_a = self._team_form(prior, away, 10) + form_boost_away

        home_prev = prior[
            (prior["home_team"] == home) | (prior["away_team"] == home)
        ].tail(1)
        away_prev = prior[
            (prior["home_team"] == away) | (prior["away_team"] == away)
        ].tail(1)
        home_rest = (
            (row["date"] - home_prev.iloc[-1]["date"]).days if not home_prev.empty else 7
        )
        away_rest = (
            (row["date"] - away_prev.iloc[-1]["date"]).days if not away_prev.empty else 7
        )
        days_rest_diff = home_rest - away_rest

        is_ko = (
            force_knockout
            if force_knockout is not None
            else bool(row.get("is_knockout", False))
            or is_knockout_stage(str(row.get("tournament", "")), str(row.get("city", "")))
        )

        conf_h = get_team_confederation(home)
        conf_a = get_team_confederation(away)
        confed_same = 1.0 if conf_h and conf_a and conf_h == conf_a else 0.0

        h2h = self._h2h_win_rate(prior, home, away)

        return np.array(
            [
                delta,
                abs(delta),
                form_5_h,
                form_5_a,
                form_10_h,
                form_10_a,
                days_rest_diff,
                float(is_ko),
                confed_same,
                h2h,
            ],
            dtype=float,
        )

    def fit(self, feature_matrix: np.ndarray, outcomes: list[str]) -> None:
        self.scaler = StandardScaler()
        x_scaled = self.scaler.fit_transform(feature_matrix)
        self.model = LogisticRegression(
            max_iter=1000,
            random_state=42,
        )
        self.model.fit(x_scaled, outcomes)

    def predict_proba_vector(self, features: np.ndarray) -> dict[str, float]:
        if self.model is None or self.scaler is None:
            delta = features[0]
            abs_delta = features[1]
            p_draw = max(0.05, min(0.45, 0.28 - abs_delta / 1200))
            p_home = 1.0 / (1.0 + 10 ** (-delta / 400.0))
            p_home = p_home * (1 - p_draw)
            p_away = max(0.0, 1.0 - p_home - p_draw)
            total = p_home + p_draw + p_away
            return {"W": p_home / total, "D": p_draw / total, "L": p_away / total}

        x = self.scaler.transform(features.reshape(1, -1))
        probs = self.model.predict_proba(x)[0]
        classes = list(self.model.classes_)
        return {cls: float(probs[classes.index(cls)]) for cls in OUTCOME_ORDER}

    def predict_match(
        self,
        home: str,
        away: str,
        match_date: pd.Timestamp,
        history_df: pd.DataFrame,
        neutral: bool = True,
        home_elo_adj: float = 0.0,
        away_elo_adj: float = 0.0,
        form_boost_home: float = 0.0,
        form_boost_away: float = 0.0,
        is_knockout: bool = False,
        elo_engine: EloEngine | None = None,
    ) -> dict[str, Any]:
        if elo_engine is None:
            engine = EloEngine()
            prior = history_df[history_df["date"] < match_date].sort_values("date")
            engine.process_dataframe(prior)
        else:
            engine = elo_engine

        elo_home = engine.get_rating(home) + (0.0 if neutral else 100.0)
        elo_away = engine.get_rating(away)

        row = pd.Series(
            {
                "date": match_date,
                "home_team": home,
                "away_team": away,
                "is_knockout": is_knockout,
            }
        )
        features = self.build_features_for_row(
            row,
            history_df,
            engine.get_rating(home),
            engine.get_rating(away),
            home_adj=home_elo_adj,
            away_adj=away_elo_adj,
            form_boost_home=form_boost_home,
            form_boost_away=form_boost_away,
            force_knockout=is_knockout,
        )
        probs = self.predict_proba_vector(features)
        predicted = max(probs, key=probs.get)
        return {
            "home_team": home,
            "away_team": away,
            "neutral": neutral,
            "elo_home": engine.get_rating(home),
            "elo_away": engine.get_rating(away),
            "probabilities": probs,
            "predicted_outcome": predicted,
            "features": dict(zip(self.feature_names, features.tolist())),
        }

    def implied_scoreline(self, probs: dict[str, float], elo_home: float, elo_away: float) -> str:
        """Most likely scoreline from the Poisson score distribution."""
        top = self.top_outcomes(probs, elo_home, elo_away, n=1)
        return top[0]["score"] if top else "1-1"

    @staticmethod
    def _poisson_pmf(k: int, lam: float) -> float:
        if lam <= 0:
            return 1.0 if k == 0 else 0.0
        return math.exp(-lam) * (lam**k) / math.factorial(k)

    def top_outcomes(
        self,
        probs: dict[str, float],
        elo_home: float,
        elo_away: float,
        n: int = 5,
        max_goals: int = 5,
    ) -> list[dict[str, float | str]]:
        """Top-N scorelines from independent Poisson rates derived from W/D/L probs."""
        mu = 2.45 + min(abs(elo_home - elo_away) / 400.0, 1.0) * 0.35
        rho_h = probs["W"] + 0.5 * probs["D"]
        rho_a = probs["L"] + 0.5 * probs["D"]
        denom = rho_h + rho_a
        if denom <= 0:
            lam_h = lam_a = mu / 2
        else:
            lam_h = mu * rho_h / denom
            lam_a = mu * rho_a / denom

        draw_boost = 1.0 + probs["D"] * 0.5
        raw: list[tuple[str, float]] = []
        for h in range(max_goals + 1):
            for a in range(max_goals + 1):
                p = self._poisson_pmf(h, lam_h) * self._poisson_pmf(a, lam_a)
                if h == a:
                    p *= draw_boost
                raw.append((f"{h}-{a}", p))

        total = sum(p for _, p in raw)
        if total <= 0:
            return [{"score": "1-1", "probability": 1.0}]

        normalized = sorted(((s, p / total) for s, p in raw), key=lambda x: -x[1])
        return [
            {"score": score, "probability": round(prob, 4)}
            for score, prob in normalized[:n]
        ]
