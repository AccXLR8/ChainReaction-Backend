from __future__ import annotations

import random
import string
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, constr
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import auth_service
from app.database.repositories import UserRepository
from app.database.session import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenUser(BaseModel):
    id: uuid.UUID
    username: str
    is_guest: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: TokenUser


class RegisterRequest(BaseModel):
    username: constr(min_length=3, max_length=64)
    password: constr(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    username: constr(min_length=3, max_length=64)
    password: constr(min_length=6, max_length=128)


class GuestRequest(BaseModel):
    username: str | None = Field(default=None, max_length=64)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(body: RegisterRequest, session: AsyncSession = Depends(get_session)):
    repo = UserRepository(session)
    existing = await repo.get_registered_by_username(body.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    password_hash = auth_service.hash_password(body.password)
    user = await repo.create(
        username=body.username,
        password_hash=password_hash,
        is_guest=False,
    )
    await session.commit()

    token = auth_service.create_access_token(user=user)
    return TokenResponse(access_token=token, user=_serialize_user(user))


@router.post("/login", response_model=TokenResponse)
async def login_user(body: LoginRequest, session: AsyncSession = Depends(get_session)):
    repo = UserRepository(session)
    user = await repo.get_by_username(body.username)
    if not user or not auth_service.verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.is_guest:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Guest accounts cannot log in with passwords")

    token = auth_service.create_access_token(user=user)
    return TokenResponse(access_token=token, user=_serialize_user(user))


@router.post("/guest", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def guest_user(body: GuestRequest | None = None, session: AsyncSession = Depends(get_session)):
    repo = UserRepository(session)
    username = _generate_guest_username(body.username if body else None)
    user = await repo.create(username=username, password_hash=None, is_guest=True)
    await session.commit()
    token = auth_service.create_access_token(user=user)
    return TokenResponse(access_token=token, user=_serialize_user(user))


def _generate_guest_username(desired: str | None = None) -> str:
    if desired:
        return desired
    suffix = "".join(random.choices(string.digits, k=6))
    return f"guest-{suffix}"


def _serialize_user(user) -> TokenUser:
    return TokenUser(id=user.id if isinstance(user.id, uuid.UUID) else uuid.UUID(str(user.id)), username=user.username, is_guest=user.is_guest)
