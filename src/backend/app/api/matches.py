from fastapi import APIRouter

from app.data.loader import get_world_cup_matches, list_world_cup_years
from app.services import tournament_match_predictions

router = APIRouter(prefix="/tournaments", tags=["tournaments"])


@router.get("")
def list_tournaments():
    return {"years": list_world_cup_years()}


@router.get("/{year}/matches")
def tournament_matches(year: int):
    wc = get_world_cup_matches(year=year)
    predictions = {f"{p['home_team']}|{p['away_team']}|{p['date']}": p for p in tournament_match_predictions(year)}

    matches = []
    for _, row in wc.iterrows():
        key = f"{row['home_team']}|{row['away_team']}|{row['date'].strftime('%Y-%m-%d')}"
        pred = predictions.get(key, {})
        matches.append(
            {
                "date": row["date"].strftime("%Y-%m-%d"),
                "home_team": row["home_team"],
                "away_team": row["away_team"],
                "home_score": int(row["home_score"]),
                "away_score": int(row["away_score"]),
                "tournament": row["tournament"],
                "city": row.get("city", ""),
                "predicted": pred.get("probabilities"),
                "predicted_outcome": pred.get("predicted"),
                "actual": pred.get("actual"),
                "correct": pred.get("correct"),
            }
        )

    matches.sort(key=lambda m: m["date"])
    correct = sum(1 for m in matches if m.get("correct"))
    return {
        "year": year,
        "matches": matches,
        "summary": {
            "total": len(matches),
            "correct": correct,
            "accuracy": round(correct / len(matches), 4) if matches else 0.0,
        },
    }
