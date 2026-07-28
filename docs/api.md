# API Overview

Base path: `/api/v1`

## Public

- `GET /health`
- `POST /auth/register`
- `POST /auth/login`

## Organization Scoped

- `GET /organizations/{organization_id}/dashboard/summary`
- `POST /organizations/{organization_id}/incidents`
- `GET /organizations/{organization_id}/incidents`
- `GET /organizations/{organization_id}/incidents/{incident_id}`
- `PATCH /organizations/{organization_id}/incidents/{incident_id}`
- `GET /organizations/{organization_id}/incidents/{incident_id}/timeline`
- `GET /organizations/{organization_id}/api-keys`
- `POST /organizations/{organization_id}/api-keys`
- `GET /organizations/{organization_id}/audit-logs`
- `GET /organizations/{organization_id}/workflows`
- `POST /organizations/{organization_id}/workflows`

## Ingestion

- `POST /alerts/ingest`

The ingest endpoint uses the `X-API-Key` header. API keys are organization
scoped and stored as hashes.

