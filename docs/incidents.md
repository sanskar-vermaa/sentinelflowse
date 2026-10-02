# Incident Management

Incidents are organization-scoped response records created by users or alert
deduplication jobs. Every incident has a severity, status, dedupe key, optional
assignee, and timeline events.

## Endpoints

- `POST /api/v1/organizations/{organization_id}/incidents`
- `GET /api/v1/organizations/{organization_id}/incidents`
- `GET /api/v1/organizations/{organization_id}/incidents/{incident_id}`
- `PATCH /api/v1/organizations/{organization_id}/incidents/{incident_id}`
- `GET /api/v1/organizations/{organization_id}/incidents/{incident_id}/timeline`
- `GET /api/v1/organizations/{organization_id}/incidents/{incident_id}/alerts`
- `POST /api/v1/organizations/{organization_id}/incidents/{incident_id}/triage`

## Status Flow

Statuses:

```txt
open -> acknowledged -> mitigated -> resolved -> archived
```

Every change to status, severity or assignee is recorded on the timeline and in the audit log, and queues `incident.updated` (and `incident.resolved`) workflows. Assignees must be members of the organization.

## Permission Model

- `incident:read` is required for list, detail, and timeline.
- `incident:write` is required for create and update.
- Viewers can read but not change incidents or request triage.

