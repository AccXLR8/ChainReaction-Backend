from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from app.games.models import PlayerClock


@dataclass
class GameClockState:
    clocks: Dict[int, PlayerClock]
    active_slot: int | None

    def snapshot(self, now: float) -> Dict[int, int]:
        return {slot: clock.snapshot(now) for slot, clock in self.clocks.items()}

    def start(self, slot: int, now: float) -> None:
        clock = self.clocks[slot]
        clock.start(now)
        self.active_slot = slot

    def stop(self, slot: int, now: float) -> None:
        clock = self.clocks[slot]
        clock.stop(now)
        if self.active_slot == slot:
            self.active_slot = None

    def switch(self, next_slot: int, now: float) -> None:
        if self.active_slot is not None:
            self.stop(self.active_slot, now)
        self.start(next_slot, now)

    def has_time(self, slot: int, now: float) -> bool:
        return self.clocks[slot].snapshot(now) > 0
