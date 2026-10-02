# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY apps/api/pyproject.toml apps/api/pyproject.toml
COPY apps/api/app apps/api/app
RUN pip install ./apps/api
COPY apps/worker apps/worker
WORKDIR /app/apps/worker

RUN useradd --create-home --uid 1000 app
USER app

CMD ["python", "-m", "sentinelflow_worker"]
