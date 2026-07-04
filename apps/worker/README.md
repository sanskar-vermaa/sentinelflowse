# SentinelFlow Worker

The worker processes alert batches, deduplicates related alerts, enriches
incidents, and executes workflow runs. The initial implementation is a
bootstrap that will be connected to Redis-backed queues in later commits.

