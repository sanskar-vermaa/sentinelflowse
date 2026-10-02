.PHONY: install api worker web migrate seed test lint format infra-up infra-down demo

install:
	cd apps/api && pip install -e ".[dev]"
	cd apps/web && npm ci

api:
	cd apps/api && uvicorn app.main:app --reload

worker:
	cd apps/worker && python -m sentinelflow_worker

web:
	cd apps/web && npm run dev

migrate:
	cd apps/api && alembic upgrade head

seed:
	cd apps/api && python -m app.db.seed

test:
	cd apps/api && pytest
	cd apps/worker && pytest
	cd apps/web && npm run lint && npm run typecheck

lint:
	cd apps/api && ruff check app tests migrations && ruff format --check app tests migrations

format:
	cd apps/api && ruff check --fix app tests migrations && ruff format app tests migrations

infra-up:
	cd infra && docker compose up --build -d

infra-down:
	cd infra && docker compose down

demo:
	./scripts/run_demo.sh
