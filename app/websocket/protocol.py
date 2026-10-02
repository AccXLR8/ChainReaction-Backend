from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ClientMessageType(str, Enum):
    AUTHENTICATE = "authenticate"
    JOIN_GAME = "join_game"
    MOVE = "move"
    PING = "ping"
    RESIGN = "resign"
    RESUME = "resume"


class ServerMessageType(str, Enum):
    CONNECTION_ACK = "connection_ack"
    GAME_READY = "game_ready"
    GAME_STARTED = "game_started"
    STATE_SNAPSHOT = "state_snapshot"
    MOVE_ACCEPTED = "move_accepted"
    MOVE_REJECTED = "move_rejected"
    CLOCK_UPDATE = "clock_update"
    GAME_FINISHED = "game_finished"
    ERROR = "error"
    PONG = "pong"


class ClientMessage(BaseModel):
    type: ClientMessageType
    payload: dict = {}


class MovePayload(BaseModel):
    cell: int
    client_move_id: Optional[str] = None


class ErrorMessage(BaseModel):
    type: ServerMessageType = ServerMessageType.ERROR
    code: str
    message: str
    request_id: Optional[str] = None
