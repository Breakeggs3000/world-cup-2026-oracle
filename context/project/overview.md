# Project overview

> Agents read this at session start.

## Name

World Cup 2026 Oracle ([world-cup-2026-oracle](https://github.com/Breakeggs3000/world-cup-2026-oracle))

## Purpose

Interactive web application for predicting international football match outcomes (Win / Draw / Loss) using real historical data, with honest walk-forward backtesting, 2026 World Cup fixture exploration, scenario tweaking, and Monte Carlo tournament simulation.

## Current status

MVP complete: FastAPI backend, React frontend, Elo + multinomial logistic model, backtest pipeline, and WC 2026 fixtures.

## Tech stack

| Layer | Choice |
|-------|--------|
| Backend | Python 3.11+, FastAPI, pandas, scikit-learn |
| Frontend | React 18, TypeScript, Vite, Recharts |
| Data | martj42/international_results (CC0), static WC 2026 fixtures JSON |
| Model | Chronological Elo + multinomial logistic regression on capped features |

## Repository map

| Path | Contents |
|------|----------|
| `src/backend/` | FastAPI app, ML models, data scripts |
| `src/frontend/` | React UI |
| `workspace/artifacts/` | Generated backtest report |
| `context/` | Project knowledge and ADRs |
| `tasks/backlog/` | Task specs |

## Success criteria

- Walk-forward backtest beats naive Elo baseline on 2023+ test split
- ~55–62% out-of-sample W/D/L accuracy (aligned with published Elo baselines)
- UI browses historical World Cups (1990–2022), WC 2026 fixtures, scenario sliders, and tournament simulation
- Leakage test passes: truncated Elo run matches full run at same cutoff date

## Contacts / ownership

Agent workspace project generated from pilot101 template.
