# Alert Ingestion

SentinelFlow accepts external alerts through `POST /api/v1/alerts/ingest`.

## Authentication

Send an organization API key in the `X-API-Key` header.

## Example Payload

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

The API stores the raw alert, builds a deterministic dedupe key, and creates an
incident for response tracking.
