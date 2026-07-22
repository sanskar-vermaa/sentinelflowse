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

## Status Flow

The first stable flow is intentionally simple:

```txt
open -> acknowledged -> mitigated -> resolved -> archived
```

Future commits will enforce transition rules. For now, status changes are
recorded as timeline events so behavior is visible and testable.

## Permission Model

- `incident:read` is required for list, detail, and timeline.
- `incident:write` is required for create and update.
- `incident:assign` will be enforced when dedicated assignment APIs are added.

