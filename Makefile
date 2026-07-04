.PHONY: api web infra-up infra-down

api:
	cd apps/api && uvicorn app.main:app --reload

web:
	cd apps/web && npm run dev

infra-up:
	cd infra && docker compose up --build

infra-down:
	cd infra && docker compose down

