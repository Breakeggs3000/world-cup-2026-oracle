from fastapi import APIRouter

from app.services import get_backtest_report

router = APIRouter(prefix="/backtest", tags=["backtest"])


@router.get("/summary")
def backtest_summary():
    report = get_backtest_report()
    return {
        "validation": report.get("validation", {}),
        "test": report.get("test", {}),
        "naive_baseline_test_accuracy": report.get("naive_baseline_test_accuracy"),
        "beats_naive_by": report.get("beats_naive_by"),
        "calibration": report.get("calibration", []),
        "world_cups": report.get("world_cups", {}),
        "confusion_matrix": report.get("confusion_matrix", {}),
        "splits": report.get("splits", {}),
    }


@router.get("/tournaments/{year}")
def backtest_tournament(year: int):
    report = get_backtest_report()
    wc = report.get("world_cups", {}).get(str(year))
    if not wc:
        return {"year": year, "metrics": None, "message": "No World Cup data for this year"}
    return {"year": year, "metrics": wc}
