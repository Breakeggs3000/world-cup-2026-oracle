"""Monte Carlo tournament simulation for WC 2026."""

from __future__ import annotations

import random
from collections import Counter, defaultdict
from typing import Any

import pandas as pd

from app.data.loader import filter_wc2026_fixtures, load_results, normalize_team
from app.model.predictor import MatchPredictor


def _sample_outcome(probs: dict[str, float], rng: random.Random) -> tuple[int, int]:
    r = rng.random()
    if r < probs["W"]:
        goals_home = rng.choice([1, 2, 3], weights=[0.45, 0.4, 0.15])
        goals_away = rng.randint(0, max(0, goals_home - 1))
        return goals_home, goals_away
    r -= probs["W"]
    if r < probs["D"]:
        g = rng.choice([0, 1, 2], weights=[0.15, 0.7, 0.15])
        return g, g
    goals_away = rng.choice([1, 2, 3], weights=[0.45, 0.4, 0.15])
    goals_home = rng.randint(0, max(0, goals_away - 1))
    return goals_home, goals_away


def _group_standings(
    fixtures: list[dict[str, Any]],
    results: dict[str, tuple[int, int]],
) -> dict[str, list[tuple[str, int, int, int]]]:
    groups: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))

    for fx in fixtures:
        if fx.get("stage") != "Group":
            continue
        gid = fx["id"]
        group = fx["group"]
        home = fx["home_team"]
        away = fx["away_team"]
        if gid in results:
            hs, aws = results[gid]
        elif fx.get("status") == "played":
            hs, aws = int(fx["home_score"]), int(fx["away_score"])
        else:
            continue

        for team, gf, ga, pts in (
            (home, hs, aws, 3 if hs > aws else 1 if hs == aws else 0),
            (away, aws, hs, 3 if aws > hs else 1 if hs == aws else 0),
        ):
            rec = groups[group][team]
            rec[0] += pts
            rec[1] += gf - ga
            rec[2] += gf
            rec[3] += 1

    standings: dict[str, list[tuple[str, int, int, int]]] = {}
    for group, teams in groups.items():
        ranked = sorted(
            teams.items(),
            key=lambda x: (x[1][0], x[1][1], x[1][2]),
            reverse=True,
        )
        standings[group] = [(t, v[0], v[1], v[2]) for t, v in ranked]
    return standings


def simulate_wc2026(
    predictor: MatchPredictor,
    history_df: pd.DataFrame,
    n_sims: int = 10_000,
    home_elo_adj: float = 0.0,
    away_elo_adj: float = 0.0,
    form_boost_home: float = 0.0,
    form_boost_away: float = 0.0,
    seed: int = 42,
) -> dict[str, Any]:
    fixtures = [f for f in filter_wc2026_fixtures("all") if f.get("stage") == "Group"]
    group_fixtures: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fx in fixtures:
        group_fixtures[fx["group"]].append(fx)

    champion_counts: Counter[str] = Counter()
    advance_counts: Counter[str] = Counter()
    rng = random.Random(seed)

    for _ in range(n_sims):
        sim_results: dict[str, tuple[int, int]] = {}
        for fx in fixtures:
            if fx.get("status") == "played":
                sim_results[fx["id"]] = (int(fx["home_score"]), int(fx["away_score"]))
                continue
            home = normalize_team(fx["home_team"])
            away = normalize_team(fx["away_team"])
            if home == "TBD" or away == "TBD":
                continue
            pred = predictor.predict_match(
                home,
                away,
                pd.Timestamp(fx["date"]),
                history_df,
                neutral=fx.get("neutral", True),
                home_elo_adj=home_elo_adj,
                away_elo_adj=away_elo_adj,
                form_boost_home=form_boost_home,
                form_boost_away=form_boost_away,
            )
            sim_results[fx["id"]] = _sample_outcome(pred["probabilities"], rng)

        standings = _group_standings(fixtures, sim_results)
        group_winners: list[str] = []
        group_runners: list[str] = []
        for group in sorted(standings.keys()):
            ranked = standings[group]
            if len(ranked) >= 1:
                group_winners.append(ranked[0][0])
                advance_counts[ranked[0][0]] += 1
            if len(ranked) >= 2:
                group_runners.append(ranked[1][0])
                advance_counts[ranked[1][0]] += 1

        # Simplified knockout: pick champion from group winners by Elo proxy (random weighted)
        candidates = group_winners + group_runners
        if candidates:
            weights = [advance_counts[c] + 1 for c in candidates]
            champion = rng.choices(candidates, weights=weights, k=1)[0]
            champion_counts[champion] += 1

    total = max(1, n_sims)
    return {
        "n_sims": n_sims,
        "champion_odds": {
            team: round(count / total, 4)
            for team, count in champion_counts.most_common(20)
        },
        "group_advance_odds": {
            team: round(count / total, 4)
            for team, count in advance_counts.most_common(48)
        },
    }


def get_trained_predictor() -> tuple[MatchPredictor, pd.DataFrame]:
    from app.model.backtest import TRAIN_END, VAL_END, build_training_dataset

    df = load_results()
    enriched, predictor = build_training_dataset(df)
    import numpy as np

    train_mask = enriched["date"] <= TRAIN_END
    x_train = np.vstack(enriched.loc[train_mask, "features"].values)
    y_train = enriched.loc[train_mask, "outcome"].tolist()
    predictor.fit(x_train, y_train)
    return predictor, df
