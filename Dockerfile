# Optional container deploy (Fly.io, Railway, Render Docker, etc.)
FROM python:3.12-slim

WORKDIR /app

# Repo root layout: backend code + workspace model artifacts
COPY src/backend/requirements.txt src/backend/requirements.txt
RUN pip install --no-cache-dir -r src/backend/requirements.txt

COPY . .

WORKDIR /app/src/backend
RUN python scripts/deploy_prepare.py

ENV PORT=8000
EXPOSE 8000

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
