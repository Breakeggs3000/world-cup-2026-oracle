# Railway / Docker deploy — repo root context
FROM python:3.12-slim

WORKDIR /app

COPY src/backend/requirements.txt src/backend/requirements.txt
RUN pip install --no-cache-dir -r src/backend/requirements.txt

COPY . .

WORKDIR /app/src/backend
# Verify only — do not train during build (Railway build VMs OOM on full retrain).
RUN python scripts/deploy_prepare.py --build

RUN chmod +x /app/docker-entrypoint.sh

ENV PORT=8000
EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
