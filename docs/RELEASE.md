# Release process

## Versioning

| Component | Source of truth | Current |
|-----------|-----------------|---------|
| API | `src/backend/app/version.py` → `API_VERSION` | 1.0.0 |
| Model | `workspace/artifacts/models/registry.json` → `active_model_version` | 1.0.0 |
| Git tag | Annotated tag `v{API_VERSION}` on release commit | v1.0.0 |

## Branches

| Branch | Purpose |
|--------|---------|
| `master` | Active development (1.1+, features, live data sync) |
| `release/1.0` | Patch fixes for the 1.0.x line only |

## Cut a release

1. Ensure `API_VERSION` and changelog are updated.
2. Commit on `master`.
3. Tag: `git tag -a v1.0.0 -m "Release 1.0.0"`
4. Branch: `git branch release/1.0 v1.0.0`
5. Push: `git push origin master release/1.0 v1.0.0`
6. Create GitHub Release from tag (notes from `CHANGELOG.md`).

## Patch on 1.0.x

```bash
git checkout release/1.0
# fix, bump API_VERSION to 1.0.1 if needed
git tag -a v1.0.1 -m "Patch 1.0.1"
git push origin release/1.0 v1.0.1
# cherry-pick to master if applicable
```

## Minor / major (new work)

Develop on `master`. Bump `API_VERSION` minor/major in `app/version.py` when routes or contracts change. Bump model with `train_model.py --bump minor`.
