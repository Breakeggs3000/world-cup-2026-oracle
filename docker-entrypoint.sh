#!/bin/sh
set -e
cd /app/src/backend
python scripts/fetch_data.py
python scripts/sync_live_data.py || true
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
