# Workflows

Workflows automate response steps when incidents change.

```json
{
  "name": "Escalate production outages",
  "trigger": "incident.created",
  "definition": {
    "conditions": {"min_severity": "high"},
    "steps": [
      {"type": "notify", "channel": "#incidents"},
      {"type": "timeline", "message": "Follow the checkout runbook"},
      {"type": "escalate", "severity": "critical"}
    ]
  }
}
```

## Triggers

| Trigger | Fires when |
| --- | --- |
| `incident.created` | An incident is created (manually or from an alert) |
| `incident.updated` | Status, severity or assignee changes |
| `incident.resolved` | Status changes to `resolved` (also fires `incident.updated`) |
| `manual` | `POST .../workflows/{id}/runs` |

`conditions.min_severity` limits a workflow to incidents at or above that severity.

## Steps

| Type | Fields | Effect |
| --- | --- | --- |
| `notify` | `channel` | Records a notification on the timeline |
| `timeline` | `message` | Adds a note to the timeline |
| `escalate` | `severity` | Raises the incident's severity (never lowers it) |

Definitions are validated on creation (422 with the reason). Up to 20 steps.

## Execution

Matching enabled workflows get a `queued` run. The [worker](worker.md) picks runs up and marks them `succeeded` or `failed` with per-step output; every run is audited. With `WORKFLOW_EXECUTION=inline` the API executes runs right after the request instead, which suits single-service deployments.
