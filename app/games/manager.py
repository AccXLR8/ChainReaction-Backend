from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Dict


class GameLockManager:
    def __init__(self) -> None:
        self._locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    def get_lock(self, game_id: str) -> asyncio.Lock:
        return self._locks[game_id]

    def release(self, game_id: str) -> None:
        self._locks.pop(game_id, None)


game_lock_manager = GameLockManager()
