"""Chronological Elo rating engine for international football."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from app.data.loader import is_knockout_stage, is_world_cup_row, outcome_label

DEFAULT_ELO = 1500.0
HOME_ADVANTAGE = 100.0

K_WORLD_CUP = 60.0
K_CONFED = 40.0
K_FRIENDLY = 20.0


@dataclass
class EloEngine:
    ratings: dict[str, float] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)

    def get_rating(self, team: str) -> float:
        return self.ratings.get(team, DEFAULT_ELO)

    def k_factor(self, tournament: str) -> float:
        t = (tournament or "").lower()
        if is_world_cup_row(tournament):
            return K_WORLD_CUP
        if "friendly" in t:
            return K_FRIENDLY
        return K_CONFED

    def goal_multiplier(self, home_score: int, away_score: int) -> float:
        margin = abs(home_score - away_score)
        if margin <= 1:
            return 1.0
        if margin == 2:
            return 1.25
        return 1.5

    def expected_score(self, rating_a: float, rating_b: float) -> float:
        return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))

    def actual_scores(self, home_score: int, away_score: int) -> tuple[float, float]:
        if home_score > away_score:
            return 1.0, 0.0
        if home_score < away_score:
            return 0.0, 1.0
        return 0.5, 0.5

    def is_neutral(self, row: pd.Series) -> bool:
        if is_world_cup_row(str(row.get("tournament", ""))):
            return True
        city = str(row.get("city", "")).strip()
        country = str(row.get("country", "")).strip()
        home = str(row.get("home_team", "")).strip()
        if not country and not city:
            return False
        return home not in country and home not in city

    def process_match(self, row: pd.Series) -> dict[str, Any]:
        home = str(row["home_team"])
        away = str(row["away_team"])
        home_score = int(row["home_score"])
        away_score = int(row["away_score"])

        elo_home_pre = self.get_rating(home)
        elo_away_pre = self.get_rating(away)

        neutral = self.is_neutral(row)
        home_eff = elo_home_pre + (0.0 if neutral else HOME_ADVANTAGE)
        away_eff = elo_away_pre

        expected_home = self.expected_score(home_eff, away_eff)
        expected_away = 1.0 - expected_home
        actual_home, actual_away = self.actual_scores(home_score, away_score)

        k = self.k_factor(str(row.get("tournament", "")))
        mult = self.goal_multiplier(home_score, away_score)
        delta_home = k * mult * (actual_home - expected_home)
        delta_away = k * mult * (actual_away - expected_away)

        self.ratings[home] = elo_home_pre + delta_home
        self.ratings[away] = elo_away_pre + delta_away

        record = {
            "date": row["date"],
            "home_team": home,
            "away_team": away,
            "home_score": home_score,
            "away_score": away_score,
            "tournament": row.get("tournament", ""),
            "city": row.get("city", ""),
            "neutral": neutral,
            "elo_home_pre": elo_home_pre,
            "elo_away_pre": elo_away_pre,
            "elo_home_post": self.ratings[home],
            "elo_away_post": self.ratings[away],
            "outcome": outcome_label(home_score, away_score),
            "is_knockout": is_knockout_stage(str(row.get("tournament", "")), str(row.get("city", ""))),
        }
        self.history.append(record)
        return record

    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        self.history = []
        for _, row in df.sort_values("date").iterrows():
            self.process_match(row)
        return pd.DataFrame(self.history)

    def snapshot_ratings(self) -> dict[str, float]:
        return dict(self.ratings)

    def ratings_at_date(self, df: pd.DataFrame, cutoff: pd.Timestamp) -> dict[str, float]:
        engine = EloEngine()
        subset = df[df["date"] < cutoff].sort_values("date")
        engine.process_dataframe(subset)
        return engine.snapshot_ratings()
