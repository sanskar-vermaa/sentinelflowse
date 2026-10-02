"""A small in-process sliding-window limiter for failed logins.

Good enough for a single API instance; behind several instances, enforce
limits at the gateway or move this to Redis.
"""

import time
from collections import defaultdict, deque
from threading import Lock


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: float, clock=time.monotonic):
        self.limit = limit
        self.window = window_seconds
        self.clock = clock
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def _prune(self, key: str, now: float) -> deque[float]:
        hits = self._hits[key]
        while hits and now - hits[0] >= self.window:
            hits.popleft()
        return hits

    def is_blocked(self, key: str) -> bool:
        with self._lock:
            return len(self._prune(key, self.clock())) >= self.limit

    def hit(self, key: str) -> None:
        with self._lock:
            now = self.clock()
            self._prune(key, now).append(now)

    def reset(self, key: str | None = None) -> None:
        with self._lock:
            if key is None:
                self._hits.clear()
            else:
                self._hits.pop(key, None)
