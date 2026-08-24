# SentinelFlow

AI-powered incident response and workflow automation platform.

SentinelFlow ingests alerts from tools such as monitoring systems, GitHub,
CI pipelines, and custom webhooks. It groups duplicate alerts, scores severity,
tracks incident timelines, and runs automation workflows for response teams.

## Apps

- `apps/api` - FastAPI service for auth, incidents, workflows, and ingestion.
- `apps/web` - Next.js dashboard for operators and admins.
- `apps/worker` - Background jobs for deduplication, enrichment, and workflows.
- `apps/ingest` - Event collectors and webhook adapters.

## Packages

- `packages/shared` - Shared contracts and constants.
- `packages/rules-engine` - Rule evaluation and severity scoring.
- `packages/ai-core` - AI triage provider abstractions.

## Local Development

The repository is intentionally structured as a production-style monorepo.
Docker, migrations, tests, and CI are added incrementally as the platform grows.

## Quick Start

```bash
cp .env.example .env
cd infra
docker compose up --build
```

Run the API locally without Docker:

```bash
cd apps/api
pip install -e . pytest httpx email-validator
uvicorn app.main:app --reload
```

Run the dashboard:

```bash
cd apps/web
npm install
npm run dev
```

Seed demo data:

```bash
make seed
```

Windows demo scripts:

```powershell
.\scripts\run_api_demo.ps1
.\scripts\run_web_demo.ps1
```

Demo user:

```txt
admin@sentinelflow.dev
sentinelflow-demo
```

## Current Capabilities

- FastAPI application shell with health, auth, and incident routes.
- SQLAlchemy domain models for organizations, alerts, incidents, and workflows.
- JWT password login foundation with role-based permission helpers.
- Incident create, list, detail, update, and timeline API contracts.
- Alert ingest, alert listing, API key management, workflows (with run history),
  audit logs, and dashboard summary.
- `GET /auth/me` for resolving a logged-in user's organization memberships.
- Next.js dashboard fully wired to the live API: login, dashboard summary,
  incidents (list + detail + timeline), alerts, workflows (list + detail + run
  history), audit log, and API key management all fetch real data instead of
  placeholder content.
- Dark, glass-panel UI with subtle 3D card interactions.

## Completion Scope

This repository is a medium-level v1 of SentinelFlow. It is intentionally sized
for portfolio use and future task work: the backend has real domain boundaries,
the frontend is fully wired to the API end-to-end, and the docs describe the
remaining production hardening work (see `docs/project-status.md`).
