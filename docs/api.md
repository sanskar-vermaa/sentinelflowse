# API reference

Base path: `/api/v1`. Interactive docs at `/docs` outside production.

Authenticated endpoints take `Authorization: Bearer <access token>`. Organization endpoints check membership and role on every request; ids from another organization return 403 (not a member) or 404 (not in this organization).

## Health

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Liveness: `{status, service, version}` |
| GET | `/health/ready` | Readiness: checks the database, 503 when unreachable |

## Auth

| Method | Path | Description |
| --- | --- | --- |
| POST | `/auth/register` | Create a user and a new organization (owner). 409 if the email exists |
| POST | `/auth/login` | Access (30 min) and refresh (14 days) tokens. 429 after repeated failures |
| POST | `/auth/refresh` | Exchange a refresh token for new tokens |
| GET | `/auth/me` | Current user and memberships |

## Organization endpoints

Prefix: `/organizations/{organization_id}`

| Method | Path | Permission | Description |
| --- | --- | --- | --- |
| GET | `/dashboard/summary` | incident:read | Open incidents, alerts processed, workflow runs |
| POST | `/incidents` | incident:write | Create an incident |
| GET | `/incidents?status=&limit=&offset=` | incident:read | List, newest activity first |
| GET | `/incidents/{id}` | incident:read | Detail |
| PATCH | `/incidents/{id}` | incident:write | Status, severity, assignee (must be a member) |
| GET | `/incidents/{id}/timeline` | incident:read | Timeline events |
| GET | `/incidents/{id}/alerts` | incident:read | Alerts grouped into the incident |
| POST | `/incidents/{id}/triage` | incident:write | AI triage; recorded on the timeline |
| GET | `/alerts` | incident:read | Recent alerts |
| GET/POST | `/workflows` | read / workflow:manage | List or create workflows |
| GET/PATCH | `/workflows/{id}` | read / workflow:manage | Detail, rename, enable/disable |
| GET | `/workflows/{id}/runs` | incident:read | Run history |
| POST | `/workflows/{id}/runs` | workflow:manage | Queue a manual run |
| GET/POST | `/api-keys` | organization:manage | List keys or create one (secret shown once) |
| GET | `/audit-logs` | organization:manage | Audit trail |

## Ingestion

`POST /alerts/ingest` with `X-API-Key: sf_...` (see [alerts.md](alerts.md)). Returns 202 with `incident_id`, `deduplicated` and `duplicate_delivery`.

## Roles

| Role | Permissions |
| --- | --- |
| owner | everything |
| admin | incidents, assignment, workflows |
| responder | incidents and assignment |
| viewer | read only |
