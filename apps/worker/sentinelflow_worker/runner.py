"""Polling worker: executes queued workflow runs.

Uses the API package's models and workflow engine, so it needs
`apps/api` installed (see infra/docker/worker.Dockerfile).
"""

from __future__ import annotations

import logging
import os
import signal
import time
from collections.abc import Callable

logger = logging.getLogger("sentinelflow.worker")


class Worker:
    def __init__(
        self,
        session_factory: Callable,
        poll_seconds: float = 2.0,
        batch_size: int = 20,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self.session_factory = session_factory
        self.poll_seconds = poll_seconds
        self.batch_size = batch_size
        self.sleep = sleep
        self.running = True

    def stop(self, *_args) -> None:
        logger.info("Shutdown requested")
        self.running = False

    def tick(self) -> int:
        from app.services.workflow_engine import WorkflowEngine

        db = self.session_factory()
        try:
            return WorkflowEngine(db).process_queued(limit=self.batch_size)
        except Exception:
            db.rollback()
            logger.exception("Worker tick failed")
            return 0
        finally:
            db.close()

    def run(self, max_ticks: int | None = None) -> None:
        ticks = 0
        while self.running and (max_ticks is None or ticks < max_ticks):
            processed = self.tick()
            if processed:
                logger.info("Processed %d workflow run(s)", processed)
            ticks += 1
            # Drain the queue quickly when busy; back off when idle.
            if processed < self.batch_size:
                self.sleep(self.poll_seconds)


def run_worker() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    from app.db.session import SessionLocal

    worker = Worker(
        SessionLocal,
        poll_seconds=float(os.environ.get("WORKER_POLL_SECONDS", "2")),
        batch_size=int(os.environ.get("WORKER_BATCH_SIZE", "20")),
    )
    signal.signal(signal.SIGTERM, worker.stop)
    signal.signal(signal.SIGINT, worker.stop)
    logger.info("SentinelFlow worker started")
    worker.run()
    logger.info("SentinelFlow worker stopped")
