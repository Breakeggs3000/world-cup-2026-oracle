from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.model.simulation import get_trained_predictor, simulate_wc2026

router = APIRouter(prefix="/api/simulate", tags=["simulation"])


class SimulateRequest(BaseModel):
    n_sims: int = Field(default=10_000, ge=100, le=100_000)
    home_elo_adj: float = 0.0
    away_elo_adj: float = 0.0
    form_boost_home: float = 0.0
    form_boost_away: float = 0.0
    seed: int = 42


@router.post("/wc2026")
def simulate_tournament(body: SimulateRequest):
    predictor, df = get_trained_predictor()
    result = simulate_wc2026(
        predictor,
        df,
        n_sims=body.n_sims,
        home_elo_adj=body.home_elo_adj,
        away_elo_adj=body.away_elo_adj,
        form_boost_home=body.form_boost_home,
        form_boost_away=body.form_boost_away,
        seed=body.seed,
    )
    return result
