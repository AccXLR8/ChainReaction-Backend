from __future__ import annotations

import asyncio
import json
from importlib import import_module
from typing import Iterable, Protocol

from app.engine.models import EngineGameState, EngineMove, EngineMoveResult


class EngineAdapter(Protocol):
    async def new_game_state(self, width: int, height: int, players: Iterable[int]) -> EngineGameState:
        ...

    async def apply_move(self, state: EngineGameState, player_slot: int, move: EngineMove) -> EngineMoveResult:
        ...


class ChainReactionEngineAdapter:
    """Adapter that bridges the PyO3 `chain_reaction` module into Python."""

    def __init__(self, module_name: str = "chain_reaction") -> None:
        self.module_name = module_name
        self._module = None

    def _ensure_module(self):
        if self._module is None:
            self._module = import_module(self.module_name)
        return self._module

    async def new_game_state(self, width: int, height: int, players: Iterable[int]) -> EngineGameState:
        module = self._ensure_module()

        def _create() -> dict:
            state = module.new_game(width=width, height=height, players=list(players))
            return json.loads(state.to_json())

        data = await asyncio.to_thread(_create)
        return EngineGameState(data=data)

    async def apply_move(self, state: EngineGameState, player_slot: int, move: EngineMove) -> EngineMoveResult:
        module = self._ensure_module()

        def _apply() -> dict:
            cr_state = module.GameState.from_json(json.dumps(state.data))
            cr_move = module.Move(row=move.row, col=move.col)
            result = module.apply_move(cr_state, player_slot, cr_move)
            payload = json.loads(result.to_json())
            return payload

        payload = await asyncio.to_thread(_apply)
        final_state = EngineGameState(data=payload["final_state"])
        return EngineMoveResult(
            final_state=final_state,
            reaction=payload["timeline"],
            result=payload["outcome"],
        )


class FakeEngineAdapter:
    """Deterministic fake for tests and local development."""

    async def new_game_state(self, width: int, height: int, players: Iterable[int]) -> EngineGameState:
        board = [[None for _ in range(width)] for _ in range(height)]
        data = {
            "width": width,
            "height": height,
            "board": board,
            "players": list(players),
            "turn_number": 0,
            "current_player": 0,
        }
        return EngineGameState(data=data)

    async def apply_move(self, state: EngineGameState, player_slot: int, move: EngineMove) -> EngineMoveResult:
        data = json.loads(json.dumps(state.data))
        history = data.setdefault("history", [])
        history.append({"row": move.row, "col": move.col, "player": player_slot})
        data["turn_number"] = data.get("turn_number", 0) + 1
        data["current_player"] = 1 - player_slot
        return EngineMoveResult(
            final_state=EngineGameState(data),
            reaction={"steps": []},
            result={"status": "ACTIVE"},
        )
