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

