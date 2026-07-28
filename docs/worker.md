# Worker

The worker is responsible for asynchronous response work:

- alert batch processing
- deduplication
- AI triage enrichment
- workflow execution
- notification retries

The v1 worker has a bootstrap job structure. It is intentionally small, but the
module boundaries are ready for Redis-backed queue integration.
