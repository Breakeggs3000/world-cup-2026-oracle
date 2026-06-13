from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services import get_history_df, get_trained_system

router = APIRouter(prefix="/predict", tags=["predictions"])


class ScenarioRequest(BaseModel):
    home: str
    away: str
    neutral: bool = True
    home_elo_adj: float = 0.0
    away_elo_adj: float = 0.0
    form_boost_home: float = 0.0
    form_boost_away: float = 0.0
    is_knockout: bool = False


@router.get("")
def predict_match(
    home: str = Query(...),
    away: str = Query(...),
    neutral: bool = Query(True),
):
    import pandas as pd

    predictor, df, _ = get_trained_system()
    result = predictor.predict_match(
        home,
        away,
        pd.Timestamp.now().normalize(),
        df,
        neutral=neutral,
    )
    result["likely_scoreline"] = predictor.implied_scoreline(
        result["probabilities"], result["elo_home"], result["elo_away"]
    )
    result["top_outcomes"] = predictor.top_outcomes(
        result["probabilities"], result["elo_home"], result["elo_away"]
    )
    return result


@router.post("/scenario")
def predict_scenario(body: ScenarioRequest):
    import pandas as pd

    predictor, df, _ = get_trained_system()
    result = predictor.predict_match(
        body.home,
        body.away,
        pd.Timestamp.now().normalize(),
        df,
        neutral=body.neutral,
        home_elo_adj=body.home_elo_adj,
        away_elo_adj=body.away_elo_adj,
        form_boost_home=body.form_boost_home,
        form_boost_away=body.form_boost_away,
        is_knockout=body.is_knockout,
    )
    elo_h = result["elo_home"] + body.home_elo_adj
    elo_a = result["elo_away"] + body.away_elo_adj
    result["likely_scoreline"] = predictor.implied_scoreline(
        result["probabilities"], elo_h, elo_a
    )
    result["top_outcomes"] = predictor.top_outcomes(
        result["probabilities"], elo_h, elo_a
    )
    return result
