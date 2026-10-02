# AI triage

`POST /api/v1/organizations/{org}/incidents/{id}/triage` returns a short summary and recommended next steps, and records them on the incident timeline as `ai.triage`. The dashboard's **AI triage** button calls it.

## Providers

| `AI_PROVIDER` | Behaviour |
| --- | --- |
| `deterministic` (default) | Severity-based playbook; no external calls, always available |
| `gemini` | Sends the incident title, severity, status, description, grouped alert sources and the last 10 timeline entries to Gemini (`GEMINI_MODEL`, default `gemini-2.5-flash`) and asks for JSON |

With Gemini, any failure (network, quota, malformed output) falls back to the playbook, so the endpoint never errors because of the model. Production refuses to start with `AI_PROVIDER=gemini` and no `GEMINI_API_KEY`.

The incident data is labelled as data, not instructions, in the prompt. Output is advisory: it is stored on the timeline and never changes incident state by itself.
