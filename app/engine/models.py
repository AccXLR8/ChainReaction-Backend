from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class EngineMove:
    row: int
    col: int


@dataclass
class EngineGameState:
    data: Dict[str, Any]

    def to_json(self) -> str:
        import json

        return json.dumps(self.data)


@dataclass
class EngineMoveResult:
    final_state: EngineGameState
    reaction: Dict[str, Any]
    result: Dict[str, Any]
