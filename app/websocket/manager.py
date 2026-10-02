from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List

from fastapi import WebSocket

from app.websocket.connection import WebSocketConnection


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: Dict[str, List[WebSocketConnection]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, user_id: str, game_id: str, player_slot: int) -> None:
        conn = WebSocketConnection(
            websocket=websocket,
            user_id=user_id,
            game_id=game_id,
            player_slot=player_slot,
            connected_at=datetime.utcnow(),
        )
        async with self._lock:
            self._connections.setdefault(game_id, []).append(conn)

    async def disconnect(self, websocket: WebSocket, game_id: str) -> None:
        async with self._lock:
            self._remove_connection(game_id, websocket)

    async def broadcast(self, game_id: str, message: dict) -> None:
        connections = list(self._connections.get(game_id, []))
        stale: List[WebSocket] = []
        for conn in connections:
            try:
                await conn.websocket.send_json(message)
            except Exception:
                stale.append(conn.websocket)
        if stale:
            async with self._lock:
                for ws in stale:
                    self._remove_connection(game_id, ws)

    async def send_to_player(self, game_id: str, player_slot: int, message: dict) -> None:
        connections = list(self._connections.get(game_id, []))
        stale: List[WebSocket] = []
        for conn in connections:
            if conn.player_slot != player_slot:
                continue
            try:
                await conn.websocket.send_json(message)
            except Exception:
                stale.append(conn.websocket)
        if stale:
            async with self._lock:
                for ws in stale:
                    self._remove_connection(game_id, ws)

    async def heartbeat(self, game_id: str, player_slot: int) -> None:
        connections = self._connections.get(game_id, [])
        for conn in connections:
            if conn.player_slot == player_slot:
                conn.last_heartbeat = datetime.utcnow()

    async def prune_stale(self, timeout_seconds: int) -> None:
        threshold = datetime.utcnow() - timedelta(seconds=timeout_seconds)
        async with self._lock:
            for game_id, conns in list(self._connections.items()):
                alive = [c for c in conns if c.last_heartbeat is None or c.last_heartbeat > threshold]
                if alive:
                    self._connections[game_id] = alive
                else:
                    self._connections.pop(game_id, None)

    def _remove_connection(self, game_id: str, websocket: WebSocket) -> None:
        conns = self._connections.get(game_id, [])
        filtered = [c for c in conns if c.websocket != websocket]
        if filtered:
            self._connections[game_id] = filtered
        else:
            self._connections.pop(game_id, None)


ws_manager = WebSocketManager()
