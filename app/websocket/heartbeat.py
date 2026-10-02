from __future__ import annotations

import asyncio
import contextlib
from typing import Awaitable, Callable


class HeartbeatMonitor:
    def __init__(self, interval_seconds: int, callback: Callable[[], Awaitable[None]]):
        self.interval_seconds = interval_seconds
        self.callback = callback
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def _run(self) -> None:
        while True:
            await asyncio.sleep(self.interval_seconds)
            await self.callback()

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None
