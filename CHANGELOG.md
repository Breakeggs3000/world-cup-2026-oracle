# Changelog

All notable changes to World Cup 2026 Oracle are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-06-13

### Added

- FastAPI backend with Elo + multinomial logistic W/D/L predictions
- React frontend: Backtest, Historical WC, WC 2026, Match Explorer, Tournament Sim
- Walk-forward backtest pipeline and committed baseline model (`elo-logistic-v1` @ **1.0.0**)
- Versioned API at `/api/v1/...` with legacy `/api/...` aliases
- `GET /api/v1/version`, semver on health and models endpoints
- Model registry with `model_version`, `--bump minor|major|patch` on `train_model.py`
- Production deploy: Railway (Docker), Vercel (frontend), Render configs
- Deployment docs: `docs/DEPLOY.md`, `docs/USAGE.md`

### Fixed

- Railway Docker build OOM (lightweight `deploy_prepare.py --build`)
- Data fingerprint stability across deploys (ignore CSV mtime)
- Non-blocking API startup (lazy model load)
- Clear frontend errors when `VITE_API_URL` missing or HTML returned

### Deployment

- **Frontend:** https://world-cup-2026-oracle.vercel.app
- **Backend:** Railway Docker (`railway.toml` + `Dockerfile`)
- **Repository:** https://github.com/Breakeggs3000/world-cup-2026-oracle

[1.0.0]: https://github.com/Breakeggs3000/world-cup-2026-oracle/releases/tag/v1.0.0

## [1.1.0] - 2026-06-13

### Added

- Live fixture sync via API-Football (primary) with optional DuckDuckGo HTML search fallback (`WEB_SEARCH_FALLBACK=1`)
- SQLite fixture store with 10-minute background sync (APScheduler)
- `GET /api/v1/sync/status`, `POST /api/v1/sync/run` (optional secret)
- WC 2026 sort/filter: `sort=datetime|date`, `order=asc|desc`, group filter (default earliest first)
- Frontend 60s polling on WC 2026 tab + manual refresh
- 15-language UI (i18next): en, zh, ko, ja, de, pt, es, fr, ar, hi, ru, it, tr, id, vi
- Betting/informational disclaimer banner + first-visit modal
- `.cursorignore` for leaner IDE context

### Changed

- API version **1.1.0** (model remains **1.0.0**)
- WC fixtures served from SQLite when available; JSON seed as bootstrap

[1.1.0]: https://github.com/Breakeggs3000/world-cup-2026-oracle/releases/tag/v1.1.0
