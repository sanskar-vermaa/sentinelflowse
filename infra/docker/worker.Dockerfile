FROM python:3.12-slim

WORKDIR /app
COPY apps/api/pyproject.toml /app/apps/api/pyproject.toml
RUN pip install --no-cache-dir -e /app/apps/api
COPY apps /app/apps
WORKDIR /app/apps/worker

CMD ["python", "-m", "sentinelflow_worker"]

