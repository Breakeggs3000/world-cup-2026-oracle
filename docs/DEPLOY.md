# Deploy World Cup 2026 Oracle

This guide walks through publishing the app to a public URL using the GitHub repo:

**https://github.com/Breakeggs3000/world-cup-2026-oracle**

Recommended layout:

| Component | Host | Why |
|-----------|------|-----|
| React frontend | [Vercel](https://vercel.com) (or Netlify) | Static Vite build, free tier, fast CDN |
| FastAPI backend | [Render](https://render.com) (or Railway / Docker) | Long-running Python process for model warm-up |

---

## 1. Push code to GitHub

From your local clone (folder may still be named `idea-board` — that is fine):

```powershell
cd path\to\idea-board
git remote add origin https://github.com/Breakeggs3000/world-cup-2026-oracle.git
git push -u origin master
```

If `origin` already exists with a different URL:

```powershell
git remote set-url origin https://github.com/Breakeggs3000/world-cup-2026-oracle.git
git push -u origin master
```

---

## 2. Deploy the backend (Render)

### Option A — Blueprint (easiest)

1. Sign in at [dashboard.render.com](https://dashboard.render.com).
2. **New** → **Blueprint** → connect GitHub → select `Breakeggs3000/world-cup-2026-oracle`.
3. Render reads `render.yaml` and creates a web service named `world-cup-2026-oracle-api`.
4. In the service **Environment** tab, set:

   | Key | Value |
   |-----|-------|
   | `ALLOWED_ORIGINS` | Your frontend URL once deployed, e.g. `https://world-cup-2026-oracle.vercel.app` |

5. Deploy. The first build takes **5–10 minutes** (pip install, CSV fetch, model verify).
6. Confirm health: `https://<your-service>.onrender.com/api/health` → `{"status":"ok","model_ready":true}`.
7. API docs: `https://<your-service>.onrender.com/docs`

Copy the backend URL — you need it for the frontend (no trailing slash).

### Option B — Manual web service

| Setting | Value |
|---------|-------|
| Runtime | Python 3.12 |
| Build command | `cd src/backend && pip install -r requirements.txt && python scripts/deploy_prepare.py` |
| Start command | `cd src/backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health check path | `/api/health` |

Set `ALLOWED_ORIGINS` as above.

### Option C — Docker (Railway, Fly.io, etc.)

Railway picks up `railway.toml` + `Dockerfile` automatically. For manual Docker:

```bash
docker build -t wc2026-oracle-api .
docker run -p 8000:8000 -e ALLOWED_ORIGINS=https://your-frontend.vercel.app wc2026-oracle-api
```

---

## 3. Deploy the frontend (Vercel)

1. Sign in at [vercel.com](https://vercel.com) → **Add New** → **Project**.
2. Import `Breakeggs3000/world-cup-2026-oracle` from GitHub.
3. Vercel detects `vercel.json` at the repo root — no custom root directory needed.
4. Before deploying, add an environment variable:

   | Key | Value |
   |-----|-------|
   | `VITE_API_URL` | Render backend URL, e.g. `https://world-cup-2026-oracle-api.onrender.com` |

5. Deploy. Vercel builds `src/frontend` and serves the SPA from `src/frontend/dist`.

### Update backend CORS

Go back to Render → set **`ALLOWED_ORIGINS`** to your Vercel URL (exact origin, no path):

```
https://world-cup-2026-oracle.vercel.app
```

Redeploy the backend if it was deployed before the frontend existed.

### Netlify alternative

1. [app.netlify.com](https://app.netlify.com) → **Add site** → import the same GitHub repo.
2. Netlify reads `netlify.toml` (`base = src/frontend`).
3. Set **`VITE_API_URL`** in Site settings → Environment variables.
4. Update `ALLOWED_ORIGINS` on Render to your Netlify URL.

---

## 4. Verify production

```bash
curl https://<api-host>/api/health
curl https://<api-host>/api/backtest/summary
```

Open the frontend URL in a browser. In DevTools → Network, requests to `https://<api-host>/api/...` should return **200** with no CORS errors.

---

## Environment variables reference

| Variable | Where | Required | Example |
|----------|-------|----------|---------|
| `VITE_API_URL` | Vercel / Netlify | Yes (prod) | `https://world-cup-2026-oracle-production.up.railway.app` (or use committed `src/frontend/.env.production`) |
| `ALLOWED_ORIGINS` | Render / Railway | Optional | `https://world-cup-2026-oracle.vercel.app` (also in backend default origins) |
| `WC_MODEL_ID` | Backend | No | `elo-logistic-v1` |
| `PORT` | Backend | Auto (host) | Render injects this |
| `API_FOOTBALL_KEY` | Railway backend | Yes (live scores) | Set in dashboard only — never commit |
| `SYNC_INTERVAL_MINUTES` | Railway backend | No | `10` |
| `FIXTURES_DB_PATH` | Railway backend | No | `/data/fixtures.db` with volume at `/data` |
| `LIVESOCCERTV_FALLBACK` | Railway backend | No | `0` (set `1` for HTML fallback) |

**API-Football free plan:** cannot fetch WC 2026 season data (error: seasons limited to 2022–2024). The app falls back to seed JSON (77 fixtures). Upgrade the API-Football plan for live scores, or keep seed data for demo.

For multiple frontends (preview + prod), comma-separate origins:

```
https://world-cup-2026-oracle.vercel.app,https://world-cup-2026-oracle-git-main.vercel.app
```

---

## What runs on deploy

`scripts/deploy_prepare.py` (called in `render.yaml` build):

1. Downloads international results CSV if missing (`scripts/fetch_data.py`).
2. Verifies committed model fingerprint; retrains only if upstream data changed.
3. Generates `backtest_report.json` if missing.

Committed in git and used in production:

- `workspace/artifacts/models/` — trained model artifacts
- `src/backend/app/data/wc2026_fixtures.json` — 2026 schedule

Not in git (fetched at build):

- `src/backend/app/data/cache/results.csv`

---

## Custom domain (optional)

**Vercel:** Project → Settings → Domains → add e.g. `oracle.example.com`. Update DNS per Vercel instructions.

**Render:** Service → Settings → Custom Domains → add e.g. `api.example.com`.

Then update:

- `VITE_API_URL` → `https://api.example.com`
- `ALLOWED_ORIGINS` → `https://oracle.example.com`

Redeploy both services.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Frontend loads, all tabs empty | Check `VITE_API_URL` is set and rebuild frontend |
| CORS error in browser | Set `ALLOWED_ORIGINS` on backend to exact frontend origin |
| `/api/health` shows `model_ready: false` | Wait for first deploy build; free Render tier may sleep — wake with a request |
| Build timeout on Render | Free tier has limits; retry deploy or upgrade plan |
| 502 after idle | Render free tier spins down; first request wakes service (~30s) |

---

## Local production smoke test

Before pushing, simulate production locally:

```powershell
# Terminal 1 — backend
cd src/backend
uv run python scripts/deploy_prepare.py
$env:ALLOWED_ORIGINS = "http://localhost:4173"
uvicorn app.main:app --port 8000

# Terminal 2 — frontend
cd src/frontend
$env:VITE_API_URL = "http://localhost:8000"
npm run build
npm run preview
```

Open http://localhost:4173 — should behave like production (no Vite proxy).
