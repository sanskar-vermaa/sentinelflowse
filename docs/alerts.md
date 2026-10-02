# Alert ingestion and deduplication

Monitoring tools, CI and webhooks send alerts to `POST /api/v1/alerts/ingest` with an organization API key in `X-API-Key`.

```json
{
  "source": "monitor",
  "external_id": "alert-123",
  "title": "Checkout latency above threshold",
  "payload": {
    "service": "checkout",
    "environment": "production",
    "severity": "high",
    "summary": "p95 latency crossed the configured threshold."
  }
}
```

`source` is one of `monitor`, `github`, `ci`, `webhook`. `payload` is free-form; `service`, `environment`, `severity` and `summary` are used when present.

## What happens

1. **Idempotency:** if this organization already received the same `source` + `external_id`, the original alert is returned with `duplicate_delivery: true`. Webhook retries never create duplicates.
2. **Dedupe key:** a hash of source, service, environment and normalised title.
3. **Grouping:** if an open (not resolved or archived) incident has the same key, the alert is attached to it, an `alert.grouped` timeline entry is added, and the incident's severity is raised if the new alert is more severe (it is never lowered). Response: `deduplicated: true`.
4. **New incident:** otherwise a new incident opens with the alert's severity (default `medium`), and `incident.created` workflows are queued.

Resolved incidents don't absorb alerts, so a recurrence after resolution opens a fresh incident.

## API keys

Keys look like `sf_<43 random characters>`, are shown once at creation, and are stored as bcrypt hashes with a 12-character lookup prefix. A key only ever writes into its own organization.
