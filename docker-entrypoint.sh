#!/bin/sh
set -e
cd /app/src/backend
# Refresh CSV at container start (fast); model artifacts ship in the image.
python scripts/fetch_data.py
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
