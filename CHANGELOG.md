# Changelog

## 1.0.0

### Security
- Replaced python-jose (CVE-2024-33663, CVE-2024-33664) and passlib with PyJWT and bcrypt
- Refresh tokens are no longer accepted as access tokens; tokens carry a type
- Production refuses weak JWT secrets; login is throttled and timing-safe
- Dashboard workflow-run count no longer includes other organizations
- Incidents can only be assigned to members of the organization
- Dashboard upgraded to Next.js 14.2.35; security headers on API and dashboard

### Fixed
- Duplicate alerts each opened a new incident; they are now grouped into the open incident
- Registering an existing email returned a 500
- Tokens with a malformed subject returned a 500
- Fresh deployments had no tables; Alembic migrations now run on API start
- docker compose pointed containers at localhost and never started the dashboard
- The API package could not be built once migrations existed
- The dashboard broke after 30 minutes because tokens were never refreshed

### Added
- Workflow engine: incident event triggers, severity conditions, notify/timeline/escalate steps, manual runs, enable/disable
- Worker that executes queued runs with SKIP LOCKED claiming and graceful shutdown
- AI triage endpoint with Gemini and a playbook fallback; grouped-alerts endpoint
- Idempotent alert ingestion for webhook retries
- Token refresh endpoint, readiness probe, request ids
- Incident page actions (acknowledge, mitigate, resolve, reopen), AI triage and alert list
- 82 API tests (SQLite and PostgreSQL in CI), worker tests, full-stack smoke test
- Dockerfiles for API, worker and dashboard; Render blueprint; deployment guide

## 0.1.0

- Monorepo with FastAPI API, Next.js dashboard, worker scaffold, incidents, alerts, workflows, API keys and audit log
