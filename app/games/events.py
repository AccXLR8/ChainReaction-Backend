from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class GameEvent:
    sequence: int
    event_type: str
    payload: Dict[str, Any]
