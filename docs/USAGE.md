# World Cup 2026 Oracle — Run & Usage Guide

Step-by-step instructions to set up, run, and use every tab in the UI.

## Quick checklist (first time)

From the repo root:

```powershell
# 1. Backend: Python env + data + backtest
cd src/backend
uv python install 3.12
uv venv .venv --python 3.12
uv pip install -r requirements.txt
uv run python scripts/fetch_data.py      # downloads ~48k international matches
uv run python scripts/run_backtest.py    # generates backtest report (optional but recommended)

# 2. Frontend: Node + deps
cd ../frontend
fnm install    # or: nvm use / install Node 22 manually
fnm use
npm install

# 3. Start both servers (easiest)
cd ../..
.\tools\scripts\start-dev.ps1
```

Open **http://localhost:5173** in your browser.

> **Important:** After running `scripts/train_model.py`, the backend loads saved artifacts in seconds. Without artifacts, the first startup rebuilds the model from scratch (~2–3 minutes). Watch the backend terminal for `Model ready.`

### Train and save model artifacts

```powershell
cd src/backend
uv run python scripts/train_model.py
```

This writes to `workspace/artifacts/models/`:

- `registry.json` — all models + active id
- `{model_id}/predictor.joblib` — fitted classifier
- `{model_id}/enriched.joblib` — precomputed features
- `{model_id}/metadata.json` — tags, hyperparameters, metrics, data fingerprint

List saved models: `GET http://localhost:8000/api/models`

Use a specific model: `$env:WC_MODEL_ID = "elo-logistic-v1"` before starting the backend.

---

## Running day-to-day

### Option A — One script (recommended)

```powershell
.\tools\scripts\start-dev.ps1
```

Opens two PowerShell windows: backend (`:8000`) and frontend (`:5173`).

### Option B — Two terminals manually

**Terminal 1 — backend** (`src/backend`):

```powershell
$env:Path = "$env:USERPROFILE\.local\bin;" + $env:Path
uv run uvicorn app.main:app --reload --port 8000
```

Wait until you see `Model ready.` in the log.

**Terminal 2 — frontend** (`src/frontend`):

```powershell
npm run dev
```

### Verify it works

| URL | What you should see |
|-----|---------------------|
| http://localhost:5173 | React UI |
| http://localhost:8000/docs | Swagger API docs |
| http://localhost:8000/api/health | `{"status":"ok","model_ready":true}` after warmup |

---

## What each tab does

### Backtest

Shows **model quality** on historical data (not live predictions):

- Test accuracy vs naive Elo baseline
- Calibration chart
- Per–World Cup accuracy (1990–2022)
- Confusion matrix

Data comes from `workspace/artifacts/backtest_report.json`. Regenerate with:

```powershell
cd src/backend
uv run python scripts/run_backtest.py
```

This tab loads quickly and does **not** need the live model.

---

### Historical WC

Browse **past World Cups (1990–2022)** with model predictions vs actual results.

For each match you see:

- Final score
- **W / D / L probability bar** (home win / draw / away win %)
- Predicted outcome vs actual (✓ or ✗)

Use the **Tournament** dropdown to pick a year and **Filter** for correct/wrong predictions only.

**Requires:** backend running + model warmed up + `results.csv` fetched.

---

### WC 2026

Shows the **2026 World Cup schedule** from `src/backend/app/data/wc2026_fixtures.json`.

Tabs:

| Tab | Content |
|-----|---------|
| **All** | Full group-stage schedule |
| **Upcoming** | Matches without scores yet |
| **Played** | Matches with entered scores + hit/miss on prediction |

Each match card shows:

- Date, group, teams, score (or `vs` if upcoming)
- **Probability bar** — W / D / L % for group-stage fixtures
- **Likely scoreline** — e.g. `2–1`
- For played games: whether the model got the outcome right

> Fixtures and scores are **curated manually** in the JSON file (not pulled from a live API). Update scores as real results come in — see [Updating WC 2026 results](#updating-wc-2026-results).

---

### Match Explorer

Pick any two teams and **tweak scenario sliders**:

- Home / away Elo adjustment (±100)
- Form boost (±0.3)
- Knockout stage toggle

Probabilities update live. Good for “what if Brazil’s form improves?” style questions.

---

### Tournament Sim

Run **Monte Carlo simulations** of WC 2026 (default 10,000 runs):

- **Champion odds** — bar chart of title probability by team
- **Group advance odds** — probability each team reaches the knockout stage

Click **Run simulations** after adjusting sliders. This can take 10–30 seconds depending on `n_sims`.

---

## Reading predictions

| Symbol | Meaning |
|--------|---------|
| **W** | Home team win |
| **D** | Draw |
| **L** | Away (visitor) win |

The colored bar shows the split, e.g. `W 52% · D 24% · L 24%`. The **predicted outcome** is whichever class has the highest probability.

---

## Updating WC 2026 results

Edit `src/backend/app/data/wc2026_fixtures.json`. For a played match, add scores:

```json
{
  "id": 13,
  "date": "2026-06-14",
  "home_team": "Belgium",
  "away_team": "Egypt",
  "stage": "group",
  "group": "G",
  "home_score": 2,
  "away_score": 1
}
```

If `home_score` / `away_score` are present, status becomes **played** automatically. Restart is not required — refresh the WC 2026 tab.

To refresh historical data (all international matches):

```powershell
cd src/backend
uv run python scripts/fetch_data.py
```

Then restart the backend (model cache resets on restart).

---

## Troubleshooting

### Tabs are empty (Historical WC, WC 2026, Match Explorer)

1. **Is the backend running?** Check http://localhost:8000/api/health
2. **Is the model ready?** Look for `Model ready.` in the backend terminal. Until then, pages show “Loading model…”
3. **Are you on the dev server?** Use `npm run dev` (port 5173), not the static `dist/` build — the dev server proxies `/api` to the backend
4. **Did you fetch data?** `src/backend/app/data/cache/results.csv` must exist (`uv run python scripts/fetch_data.py`)

### Backtest tab shows an error

Run the backtest script once:

```powershell
cd src/backend
uv run python scripts/run_backtest.py
```

### `fnm` not found

Install fnm (`winget install Schniz.fnm`) or use Node 22 another way. The frontend still works if `node`/`npm` are on PATH.

### `uv` not found

Install uv: https://docs.astral.sh/uv/getting-started/installation/

### Requests feel slow after restart

Expected — the model rebuilds once per backend process (~2–3 min). Subsequent requests in the same session are fast.

---

## API reference (optional)

Full interactive docs: http://localhost:8000/docs

| Endpoint | Use |
|----------|-----|
| `GET /api/backtest/summary` | Backtest metrics |
| `GET /api/tournaments/{year}/matches` | Historical WC with predictions |
| `GET /api/wc2026/fixtures?status=all\|upcoming\|played` | 2026 schedule + probabilities |
| `GET /api/predict?home=&away=` | Single match prediction |
| `POST /api/predict/scenario` | Scenario sliders (Match Explorer) |
| `POST /api/simulate/wc2026` | Monte Carlo tournament sim |
