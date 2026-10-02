# Worker

`apps/worker` executes queued workflow runs.

```bash
pip install -e apps/api -e apps/worker
DATABASE_URL=... python -m sentinelflow_worker
```

- Polls every `WORKER_POLL_SECONDS` (default 2) and claims up to `WORKER_BATCH_SIZE` (default 20) runs; drains back-to-back while the queue is full.
- On PostgreSQL runs are claimed with `SELECT ... FOR UPDATE SKIP LOCKED`, so several workers can run concurrently without double execution.
- A failing step marks the run `failed` with the error in `output_payload`; a database error in one tick is logged and retried on the next.
- Stops cleanly on `SIGTERM`/`SIGINT`.
