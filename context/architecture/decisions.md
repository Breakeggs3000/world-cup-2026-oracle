# Architecture decisions

Record significant technical decisions here. Use the template below for each entry.

---

## ADR-000: Agent workspace layout

**Status:** Accepted  
**Date:** 2026-06-13

### Context

The repo needs a structure that supports Cursor, Copilot, and multi-agent orchestration without mixing scratch work, durable knowledge, and source code.

### Decision

Adopt a layered layout:

- `agents/` — roles and crews
- `context/` — curated knowledge
- `memory/` — agent-learned facts
- `workspace/` — ephemeral and generated files
- `src/` — application code
- `AGENTS.md` — single entry point for agents

### Consequences

- Clear boundaries reduce accidental commits of scratch data
- Orchestrators can load `agents/registry.yaml` as machine-readable config
- Humans maintain `context/`; agents may propose updates via PRs

---

## ADR-001: Template repo vs project repos

**Status:** Accepted  
**Date:** 2026-06-13

### Context

Multiple vibe-coding experiments in one repo pollute `context/`, `memory/`, and agent focus. Agent boilerplate (git safety, onboarding) would repeat in every clone unless layered.

### Decision

- Keep `pilot101` as the **canonical template** — no real product code in `src/`.
- **One repo per product**, created via `tools/scripts/new-agent-project.py`.
- **Three config layers:**
  - User: `~/.cursor/rules/`, `~/.cursor/skills/` (universal)
  - Template: this repo (structure, roles, policies)
  - Project: generated repo (`context/`, product-specific `.cursor/rules/`)

### Consequences

- Agents stay scoped to one product context per repo
- Template improvements propagate via generator or cherry-pick
- User-level Cursor rules are not duplicated in each project

---

## ADR-002: World Cup 2026 Oracle stack

**Status:** Accepted  
**Date:** 2026-06-13

### Context

The project evolved from the pilot101 agent-workspace template into World Cup 2026 Oracle — a football prediction app requiring ML backtesting, an API, and an interactive UI.

### Decision

- **Backend:** Python FastAPI under `src/backend/` with Elo engine + multinomial logistic head
- **Frontend:** React 18 + TypeScript + Vite + Recharts under `src/frontend/`
- **Data:** martj42 international results CSV (cached locally); static `wc2026_fixtures.json` and `team_aliases.json`
- **Evaluation:** Walk-forward temporal splits (train ≤2017, val 2018–2022, test 2023+); report to `workspace/artifacts/backtest_report.json`
- **Stretch:** Monte Carlo group-stage simulation with simplified knockout champion selection

### Consequences

- No runtime scraping; 2026 schedule updates are manual JSON edits
- Model complexity capped at Elo+logit unless validation shows >0.5% gain from boosting (not pursued)
- Vite dev server proxies `/api` to FastAPI on port 8000

---

## ADR-003: Versioned model artifact registry

**Status:** Accepted  
**Date:** 2026-06-13

### Context

Retraining from scratch on every API cold start is slow (~minutes). Future work (cross-validation, ensembles, RL) requires multiple persisted model checkpoints with metadata and comparable metrics.

### Decision

- Store trained bundles under `workspace/artifacts/models/{model_id}/`:
  - `predictor.joblib` (sklearn head + scaler)
  - `enriched.joblib` (precomputed feature matrix for evaluation)
  - `elo_ratings.json`, `metrics.json`, `metadata.json`
- Maintain `registry.json` with `active_model_id` and per-model tags, hyperparameters, and data fingerprint
- API loads active artifact when fingerprint matches `results.csv`; fallback to live training if missing/stale
- `scripts/train_model.py` trains baseline and registers artifact; `GET /api/v1/models` lists registry
- Runtime override via `WC_MODEL_ID` environment variable

### Consequences

- First startup after `train_model.py` is fast (seconds vs minutes)
- Git tracks baseline model artifacts for reproducibility; retrain when data fingerprint changes
- New model families add a directory + registry entry without changing API surface

---

## ADR-004: Semver for API and model artifacts

**Status:** Accepted  
**Date:** 2026-06-13

### Context

Live data and new model families will ship incrementally. Clients need stable routes and a clear way to know which model produced a prediction.

### Decision

- **API:** version constant in `app/version.py` (currently **1.0.0**). Routes mounted at `/api/v1/...`; legacy `/api/...` aliases preserved.
- **Models:** each registry entry carries **`model_version`** semver (currently **1.0.0** for `elo-logistic-v1`). Registry tracks `active_model_version` and `api_version`.
- **Bump policy:** minor for retrains/same family; major for new families or breaking feature sets; patch for metadata-only fixes.
- **Discovery:** `GET /api/v1/version` and version fields on `/api/v1/health` and `/api/v1/models`.
- **CLI:** `train_model.py --bump minor|major|patch` or `--model-version X.Y.Z`.

### Consequences

- Frontend targets `/api/v1` by default (`VITE_API_VERSION` override optional).
- Breaking API changes require major API bump and optionally `/api/v2`.
- Model major version should align with API major when feature contracts change.

---

## ADR-005: Live fixture sync (API-Football + SQLite)

**Status:** Accepted  
**Date:** 2026-06-13

### Context

WC 2026 scores were manually edited in JSON. v1.1 needs periodic updates without redeploy.

### Decision

- SQLite store at `FIXTURES_DB_PATH` (Railway volume `/data/fixtures.db`)
- Primary provider: API-Football (`API_FOOTBALL_KEY`)
- Fallback: DuckDuckGo HTML search when `WEB_SEARCH_FALLBACK=1` and API-Football fails (updates scores on known fixtures only)
- APScheduler interval sync (default 10 min); seed from JSON when DB empty
- API exposes `GET /api/v1/sync/status`; model version unchanged at 1.0.0

### Consequences

- Railway needs volume mount + API key in env
- Scraping fallback is brittle; prefer API-Football
- API semver bumped to **1.1.0**; model semver unchanged

---

## Template for new ADRs

```markdown
## ADR-NNN: Title

**Status:** Proposed | Accepted | Superseded  
**Date:** YYYY-MM-DD

### Context
Why this decision is needed.

### Decision
What we chose.

### Consequences
Tradeoffs and follow-ups.
```
