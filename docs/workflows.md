# Workflows

Workflows model response automation. A workflow has:

- `name`
- `trigger`
- `definition`
- `is_enabled`

## Example Definition

```json
{
  "steps": [
    { "type": "notify", "channel": "on-call" },
    { "type": "timeline", "message": "Runbook started" }
  ]
}
```

The v1 backend stores workflow definitions and can queue workflow runs. Future
hardening can add a real executor that processes each step through Redis.
