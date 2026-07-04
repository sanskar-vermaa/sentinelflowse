# Architecture

SentinelFlow is a multi-tenant incident response platform built around event
ingestion, incident lifecycle management, and workflow automation.

## Request Path

1. External systems send alerts to ingest adapters or signed API endpoints.
2. The API validates the event and stores the normalized alert.
3. The worker calculates severity and dedupe keys.
4. Matching alerts are grouped into an incident.
5. Workflows run against incident state changes.
6. Operators use the web dashboard to assign, mitigate, and resolve incidents.

## Core Boundaries

- API owns authentication, authorization, incidents, alerts, workflows, and audit logs.
- Worker owns asynchronous enrichment, dedupe, notification, and workflow execution.
- Rules engine owns deterministic severity and routing decisions.
- AI core owns triage suggestions through provider adapters.
- Web owns operator workflows and admin views.

## Design Goals

- Every record is scoped by organization.
- Incident state transitions are auditable.
- Worker retries must be idempotent.
- Rule execution should be deterministic before AI enrichment is applied.
- AI output should be treated as advisory, never as the source of truth.

