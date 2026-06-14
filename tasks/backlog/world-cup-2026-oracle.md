# Task: World Cup 2026 Oracle

**Status:** Done  
**Created:** 2026-06-13

## Goal

Build a World Cup match prediction system with honest backtesting, FastAPI backend, and React UI.

## Deliverables

- [x] Data pipeline: fetch martj42 CSV, team aliases, WC 2026 fixtures, loader
- [x] Elo engine with tournament K-factors and neutral-venue handling
- [x] Multinomial logistic predictor + walk-forward backtest + leakage test
- [x] FastAPI endpoints (backtest, tournaments, predict, wc2026, simulate)
- [x] React pages: Backtest, Historical WC, WC 2026, Match Explorer, Tournament Sim
- [x] Documentation and ADR updates

## Verification

```bash
cd src/backend
python scripts/fetch_data.py
python scripts/run_backtest.py
pytest
uvicorn app.main:app --port 8000

cd ../frontend
npm run dev
```

## Notes

- 2026 fixtures are static JSON; patch scores as the tournament progresses.
- Simulation uses simplified knockout (group top-2 → weighted champion pick).
