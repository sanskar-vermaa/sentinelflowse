# SentinelFlow Worker

Executes queued workflow runs. When an incident is created, updated or resolved, the API queues a run for every enabled workflow whose trigger matches; the worker polls for queued runs, executes their steps (`notify`, `timeline`, `escalate`) and records the results on the incident timeline and in the audit log.

```bash
pip install -e ../api -e .
DATABASE_URL=... python -m sentinelflow_worker
```

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | – | Same database as the API |
| `WORKER_POLL_SECONDS` | `2` | Pause between polls when the queue is empty |
| `WORKER_BATCH_SIZE` | `20` | Runs claimed per poll |

On Postgres runs are claimed with `FOR UPDATE SKIP LOCKED`, so several workers can run side by side. The worker stops cleanly on `SIGTERM`.

For a single-service deployment, set `WORKFLOW_EXECUTION=inline` on the API instead and skip the worker.

```bash
pytest   # worker tests (uses a temporary SQLite database)
```
