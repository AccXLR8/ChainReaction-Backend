import uuid

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.matchmaking.service import matchmaking_service

router = APIRouter()


@router.post("/join")
async def join_matchmaking(user: User = Depends(get_current_user)):
    await matchmaking_service.join_queue(uuid.UUID(user.id))
    return {"status": "queued"}


@router.post("/leave")
async def leave_matchmaking(user: User = Depends(get_current_user)):
    await matchmaking_service.leave_queue(uuid.UUID(user.id))
    return {"status": "left"}
