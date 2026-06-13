# Versioned model artifacts

Each trained model is stored under `{model_id}/` with semver **`model_version`** (e.g. `1.0.0`).

| File | Purpose |
|------|---------|
| `metadata.json` | Registry entry: **model_version**, algorithm, splits, tags, data fingerprint |
| `metrics.json` | Validation/test metrics from walk-forward backtest |
| `predictor.joblib` | Fitted sklearn classifier + scaler |
| `enriched.joblib` | Precomputed feature rows for fast historical evaluation |
| `elo_ratings.json` | Elo snapshot at train cutoff |

Root `registry.json` tracks `active_model_id`, `active_model_version`, and `api_version`.

## Versioning rules

| Change | Bump | Example |
|--------|------|---------|
| Retrain same family, same features | **minor** | `1.0.0` → `1.1.0` |
| Bugfix / same weights, metadata only | **patch** | `1.0.0` → `1.0.1` |
| New model family or breaking feature set | **major** | `1.x` → `2.0.0` |

API version (`app/version.py`, currently **1.0.0**) bumps on route/response contract changes.

## Train or bump

```powershell
cd src/backend
uv run python scripts/train_model.py                          # v1.0.0 (default)
uv run python scripts/train_model.py --bump minor               # 1.0.0 → 1.1.0
uv run python scripts/train_model.py --model-version 2.0.0 --model-id elo-xgb-v2
```

## API

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/version` | API + active model versions |
| `GET /api/v1/models` | Registry with `api_version`, `active_model_version` |
| `GET /api/v1/health` | Health + version fields |

Legacy `/api/...` paths remain aliases of `/api/v1/...`.

Select a model at runtime: `$env:WC_MODEL_ID = "elo-logistic-v1"`
