# SentinelFlow

Incident response and workflow automation for engineering teams. SentinelFlow ingests alerts from monitoring, CI and webhooks, groups duplicates into a single incident, tracks every change on a timeline, runs response automations, and suggests next steps with AI triage.

**Stack:** FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL · Next.js 14 · TypeScript · Gemini (optional) · pytest · Docker · GitHub Actions

## Features

- **Alert ingestion** with organization API keys, idempotent re-delivery, and deduplication that groups matching alerts into the open incident and escalates its severity when needed
- **Incidents** with status flow (open → acknowledged → mitigated → resolved → archived), severity, assignees, a full timeline and filters
- **Workflow automation:** triggers on incident created/updated/resolved or manual runs, severity conditions, `notify` / `timeline` / `escalate` steps, executed by a background worker with `SKIP LOCKED` claiming
- **AI triage:** Gemini summary and next steps grounded in the incident, its alerts and timeline, with a deterministic playbook fallback
- **Multi-tenant RBAC:** owner, admin, responder and viewer roles; every query scoped to the organization
- **Audit log** of incident changes, alert grouping and workflow runs
- **Dashboard:** login with automatic token refresh, summary, incidents with actions and triage, alerts, workflows and run history, audit log, API key management
- **Security:** bcrypt, short-lived JWTs with refresh, login throttling, production config checks, security headers, request ids

## Quick start

### Docker (full stack)

```bash
cd infra
docker compose up --build
docker compose exec api python -m app.db.seed   # demo data
```

Dashboard: <http://localhost:3000> (demo login `admin@sentinelflow.dev` / `sentinelflow-demo`) · API docs: <http://localhost:8000/docs>

### Local demo without Docker

```bash
./scripts/run_demo.sh          # macOS / Linux
.\scripts\run_api_demo.ps1     # Windows (then run_web_demo.ps1)
```

Uses SQLite and runs workflows inside the API, so no Postgres or worker is needed.

### Send an alert

```bash
curl -X POST localhost:8000/api/v1/alerts/ingest \
  -H "X-API-Key: sf_..." -H "Content-Type: application/json" \
  -d '{"source":"monitor","external_id":"a-1","title":"High error rate",
       "payload":{"service":"checkout","environment":"production","severity":"high"}}'
```

Create the API key under **Settings** in the dashboard. Send it twice with a different `external_id` and both alerts land in the same incident.

## Repository layout

```
apps/
  api/        FastAPI service: auth, incidents, alerts, workflows, triage, audit (+ Alembic migrations)
  worker/     executes queued workflow runs
  web/        Next.js dashboard
  ingest/     notes for future collector adapters
packages/     shared TypeScript contracts, rules and AI helpers
infra/        Dockerfiles and docker-compose
docs/         architecture, API, alerts, workflows, triage, deployment
```

## Configuration

See [`.env.example`](.env.example). The essentials:

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | PostgreSQL (`postgresql+psycopg://...`) or SQLite for demos |
| `JWT_SECRET` | 32+ random characters (enforced when `APP_ENV=production`) |
| `WEB_ORIGIN` | Dashboard origin(s) allowed by CORS |
| `WORKFLOW_EXECUTION` | `worker` (default) or `inline` |
| `AI_PROVIDER`, `GEMINI_API_KEY` | `deterministic` or `gemini` |
| `NEXT_PUBLIC_API_BASE_URL` | API URL used by the dashboard |

## Testing

```bash
make test        # API, worker and dashboard checks
make lint
```

- **API:** 82 tests at 95% coverage: auth and token handling, tenant isolation and roles, deduplication, workflows, triage (with a mocked Gemini), migrations and health checks
- **CI** runs the API suite on SQLite **and PostgreSQL**, verifies migrations with `alembic check`, tests the worker, lints/type-checks/builds the dashboard, then boots the whole stack with Docker Compose and checks that duplicate alerts form one incident and the worker executes the triggered workflow

## Deployment

[docs/deployment.md](docs/deployment.md) covers Docker Compose, Render ([`render.yaml`](render.yaml)) and the dashboard on Vercel.

## Documentation

[Architecture](docs/architecture.md) · [API](docs/api.md) · [Alerts](docs/alerts.md) · [Incidents](docs/incidents.md) · [Workflows](docs/workflows.md) · [AI triage](docs/ai-triage.md) · [Worker](docs/worker.md) · [Auth](docs/auth.md) · [Security](SECURITY.md) · [Changelog](CHANGELOG.md)

## License

[MIT](LICENSE)
