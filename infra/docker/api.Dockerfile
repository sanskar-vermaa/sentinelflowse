# syntax=docker/dockerfile:1
FROM python:3.15-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app/apps/api
COPY apps/api/pyproject.toml ./
COPY apps/api/app ./app
RUN pip install .
COPY apps/api/alembic.ini ./
COPY apps/api/migrations ./migrations

RUN useradd --create-home --uid 1000 app
USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/api/v1/health/ready')"

# Apply migrations, then serve. Set RUN_MIGRATIONS=0 to manage them separately.
CMD ["sh", "-c", "if [ \"${RUN_MIGRATIONS:-1}\" = 1 ]; then alembic upgrade head; fi && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers"]
