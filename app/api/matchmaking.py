import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.service import auth_service
from app.database.repositories import UserRepository
from app.database.session import get_session
from app.games.service import game_service
from app.matchmaking.service import matchmaking_service

router = APIRouter()


@router.post("/join")
async def join_matchmaking(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    pair = await matchmaking_service.join_queue(uuid.UUID(user.id))
    if pair:
        game = await _create_match_for_pair(session, pair)
        await session.commit()
        player_ids = [uuid.UUID(pid) for pid in pair]
        await matchmaking_service.save_assignment(player_ids[0], game.id)
        await matchmaking_service.save_assignment(player_ids[1], game.id)
    else:
        await session.commit()

    assignment = await matchmaking_service.pop_assignment(uuid.UUID(user.id))
    if assignment:
        return {"status": "matched", "game_id": assignment}
    return {"status": "queued"}


@router.get("/status")
async def matchmaking_status(user: User = Depends(get_current_user)):
    assignment = await matchmaking_service.pop_assignment(uuid.UUID(user.id))
    if assignment:
        return {"status": "matched", "game_id": assignment}
    return {"status": "queued"}


@router.post("/leave")
async def leave_matchmaking(user: User = Depends(get_current_user)):
    await matchmaking_service.leave_queue(uuid.UUID(user.id))
    await matchmaking_service.pop_assignment(uuid.UUID(user.id))
    return {"status": "left"}


async def _create_match_for_pair(session: AsyncSession, pair: tuple[str, str]):
    repo = UserRepository(session)
    player_models = []
    for player_id in pair:
        user_model = await repo.get(uuid.UUID(player_id))
        if not user_model:
            raise HTTPException(status_code=404, detail=f"User {player_id} not found")
        player_models.append(user_model)

    auth_players = [auth_service.model_to_user(model) for model in player_models]
    game = await game_service.create_game(session, auth_players[0])
    await game_service.join_game(session, game.id, auth_players[1], preferred_slot=1)
    return game
