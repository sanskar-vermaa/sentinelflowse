# Deployment

## Docker Compose (single host)

```bash
cd infra
JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(48))") docker compose up --build -d
docker compose exec api python -m app.db.seed   # optional demo data
```

Postgres, the API (applies migrations on start), the worker and the dashboard. Set `APP_ENV=production`, `WEB_ORIGIN` and `NEXT_PUBLIC_API_BASE_URL` for a public host and put a TLS proxy in front.

## Render

`render.yaml` creates a Postgres database, the API and the dashboard. After the first deploy, set `WEB_ORIGIN` on the API to the dashboard URL and `NEXT_PUBLIC_API_BASE_URL` on the dashboard to `<api url>/api/v1`, then redeploy the dashboard (the URL is baked in at build time). Free plans have no background workers, so the blueprint sets `WORKFLOW_EXECUTION=inline`.

## Dashboard on Vercel

Import the repository with **Root Directory** `apps/web` and set `NEXT_PUBLIC_API_BASE_URL`. Add the Vercel URL to the API's `WEB_ORIGIN`. The API and worker need a container host (Render, Fly.io, Railway, ECS…).

## Production checklist

- `APP_ENV=production` (disables API docs, enforces the secret check)
- `JWT_SECRET` of 32+ random characters
- `WEB_ORIGIN` set to the dashboard origin(s), comma-separated
- Database backups
- One worker per region, or more (runs are claimed with `SKIP LOCKED`)
- `RUN_MIGRATIONS=0` on all but one API instance if you scale horizontally, or run `alembic upgrade head` as a release step
