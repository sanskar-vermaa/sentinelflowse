# Architecture

SentinelFlow is a multi-tenant incident response platform built around event
ingestion, incident lifecycle management, and workflow automation.

## Request Path

1. External systems send alerts to `POST /alerts/ingest` with an organization API key.
2. The API stores the alert, computes a dedupe key and either groups it into the matching open incident or opens a new one.
3. Incident changes queue runs for matching workflows.
4. The worker executes queued runs and records each step on the incident timeline.
5. Operators use the dashboard to acknowledge, triage (with AI suggestions), mitigate and resolve incidents.

## Core Boundaries

- API owns authentication, authorization, incidents, alerts, workflows, and audit logs.
- Worker owns workflow execution.
- Rules engine owns deterministic severity and routing decisions.
- AI core owns triage suggestions through provider adapters.
- Web owns operator workflows and admin views.

## Design Goals

- Every record is scoped by organization.
- Incident state transitions are auditable.
- Worker retries must be idempotent.
- Rule execution should be deterministic before AI enrichment is applied.
- AI output should be treated as advisory, never as the source of truth.


## Components

```
                  X-API-Key                    Bearer JWT
 monitors / CI ─────────────► API (FastAPI) ◄────────────── Dashboard (Next.js)
                                  │
                                  ▼
                            PostgreSQL ◄──── Worker (queued workflow runs)
                                  ▲
                                  └── Alembic migrations
```

- Multi-tenancy: every table carries `organization_id`; every query filters by it.
- Auth: bcrypt passwords, short-lived access tokens, refresh tokens, per-email+IP login throttling.
- Audit: incident changes, alert grouping and workflow runs write audit records.
- `packages/` holds shared TypeScript contracts plus rule and AI helper libraries for future ingest adapters.
