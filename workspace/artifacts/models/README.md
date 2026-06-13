# Versioned model artifacts

Each trained model is stored under `{model_id}/` with:

| File | Purpose |
|------|---------|
| `metadata.json` | Registry entry: algorithm, splits, tags, data fingerprint, hyperparameters |
| `metrics.json` | Validation/test metrics from walk-forward backtest |
| `predictor.joblib` | Fitted sklearn classifier + scaler |
| `enriched.joblib` | Precomputed feature rows for fast historical evaluation |
| `elo_ratings.json` | Elo snapshot at train cutoff |

The root `registry.json` lists all models and the `active_model_id` used by the API.

Train or refresh the baseline:

```powershell
cd src/backend
uv run python scripts/train_model.py
```

List models via API: `GET /api/models`

Select a model at runtime: `$env:WC_MODEL_ID = "elo-logistic-v1"`

Future work: add alternate families here (e.g. gradient boosting, ensemble stacks) for cross-validation and RL experiments.
