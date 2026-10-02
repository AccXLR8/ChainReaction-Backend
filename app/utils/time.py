import time
from typing import Protocol


class Clock(Protocol):
    def now(self) -> float:  # seconds, monotonic
        ...


class MonotonicClock:
    def now(self) -> float:
        return time.monotonic()


class UTCClock:
    def now(self) -> float:
        return time.time()
