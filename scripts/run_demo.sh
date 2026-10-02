#!/usr/bin/env sh
# Starts the API (SQLite, inline workflows) and the dashboard for a local demo.
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd)

cd "$ROOT/apps/api"
[ -f .env ] || cp .env.demo.example .env
python -m pip install -q -e ".[dev]"
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --port 8000 &
API_PID=$!
trap 'kill $API_PID' EXIT

cd "$ROOT/apps/web"
[ -d node_modules ] || npm ci
npm run dev
