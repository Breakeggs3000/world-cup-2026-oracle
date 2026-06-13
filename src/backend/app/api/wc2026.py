from collections import defaultdict

from fastapi import APIRouter, Query

from app.data.loader import filter_wc2026_fixtures, is_group_stage, normalize_team, outcome_label
from app.services import get_trained_system
from app.sync.service import sync_status

router = APIRouter(prefix="/wc2026", tags=["wc2026"])


def _compute_standings(fixtures: list[dict]) -> dict[str, list[dict]]:
    tables: dict[str, dict[str, dict]] = defaultdict(lambda: defaultdict(lambda: {
        "played": 0, "won": 0, "drawn": 0, "lost": 0, "gf": 0, "ga": 0, "points": 0,
    }))

    for fx in fixtures:
        if fx.get("stage") != "Group" or fx.get("status") != "played":
            continue
        group = fx["group"]
        home, away = fx["home_team"], fx["away_team"]
        hs, aws = int(fx["home_score"]), int(fx["away_score"])

        for team, gf, ga, w, d, l, pts in (
            (home, hs, aws, hs > aws, hs == aws, hs < aws, 3 if hs > aws else 1 if hs == aws else 0),
            (away, aws, hs, aws > hs, hs == aws, aws < hs, 3 if aws > hs else 1 if hs == aws else 0),
        ):
            rec = tables[group][team]
            rec["played"] += 1
            rec["won"] += int(w)
            rec["drawn"] += int(d)
            rec["lost"] += int(l)
            rec["gf"] += gf
            rec["ga"] += ga
            rec["points"] += pts

    standings = {}
    for group, teams in tables.items():
        ranked = sorted(
            teams.items(),
            key=lambda x: (x[1]["points"], x[1]["gf"] - x[1]["ga"], x[1]["gf"]),
            reverse=True,
        )
        standings[group] = [{"team": t, **stats} for t, stats in ranked]
    return standings


@router.get("/fixtures")
def wc2026_fixtures(
    status: str = Query("all", pattern="^(all|upcoming|played)$"),
    sort: str = Query("datetime", pattern="^(datetime|date)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    group: str | None = Query(None, min_length=1, max_length=2),
    stage: str | None = None,
):
    import pandas as pd

    fixtures = filter_wc2026_fixtures(status, group=group, stage=stage, sort=sort, order=order)
    meta = sync_status()
    predictor, df, _ = get_trained_system()

    from app.model.elo import EloEngine

    elo_engine = EloEngine()
    elo_engine.process_dataframe(df.sort_values("date"))

    enriched = []
    for fx in fixtures:
        item = dict(fx)
        home = normalize_team(fx["home_team"])
        away = normalize_team(fx["away_team"])
        if home and away and home != "TBD" and away != "TBD":
            pred = predictor.predict_match(
                home,
                away,
                pd.Timestamp(fx["date"]),
                df,
                neutral=fx.get("neutral", True),
                is_knockout=not is_group_stage(fx.get("stage")),
                elo_engine=elo_engine,
            )
            item["probabilities"] = pred["probabilities"]
            item["predicted_outcome"] = pred["predicted_outcome"]
            item["likely_scoreline"] = predictor.implied_scoreline(
                pred["probabilities"], pred["elo_home"], pred["elo_away"]
            )
            item["top_outcomes"] = predictor.top_outcomes(
                pred["probabilities"], pred["elo_home"], pred["elo_away"]
            )
            if fx.get("status") == "played":
                actual = outcome_label(int(fx["home_score"]), int(fx["away_score"]))
                item["actual_outcome"] = actual
                item["prediction_correct"] = pred["predicted_outcome"] == actual
        enriched.append(item)

    last = meta.get("last_sync") or {}
    return {
        "fixtures": enriched,
        "count": len(enriched),
        "sort": sort,
        "order": order,
        "last_synced_at": last.get("finished_at") or last.get("started_at"),
        "data_source": meta.get("data_source", "seed"),
    }


@router.get("/standings")
def wc2026_standings():
    fixtures = filter_wc2026_fixtures("all", sort="datetime", order="asc")
    return {"standings": _compute_standings(fixtures)}
