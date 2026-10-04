from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.auth.models import User
from app.config.settings import get_settings
from app.database import models as db


class AuthenticationError(Exception):
    """Raised when a token cannot be validated."""


class AuthService:
    def __init__(self) -> None:
        self._algorithm = "HS256"
        self._password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self._token_ttl = timedelta(hours=24)

    async def authenticate(self, token: str) -> User:
        payload = self._decode_token(token)
        now = datetime.utcnow()
        return User(
            id=payload["sub"],
            username=payload["username"],
            created_at=now,
            updated_at=now,
            is_active=payload.get("is_active", True),
            is_bot=payload.get("is_bot", False),
            is_guest=payload.get("is_guest", False),
        )

    def hash_password(self, password: str) -> str:
        return self._password_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str | None) -> bool:
        if not hashed_password:
            return False
        return self._password_context.verify(plain_password, hashed_password)

    def create_access_token(self, *, user: db.UserModel | User) -> str:
        payload = self._build_payload(user)
        settings = get_settings()
        return jwt.encode(payload, settings.secret_key, algorithm=self._algorithm)

    def _build_payload(self, user: db.UserModel | User) -> dict[str, Any]:
        if isinstance(user, db.UserModel):
            user_id = str(user.id)
            username = user.username
            is_guest = user.is_guest
        else:
            user_id = user.id
            username = user.username
            is_guest = getattr(user, "is_guest", False)
        now = datetime.utcnow()
        expire = now + self._token_ttl
        return {
            "sub": user_id,
            "username": username,
            "is_guest": is_guest,
            "is_active": True,
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        }

    def _decode_token(self, token: str) -> dict[str, Any]:
        if not token:
            raise AuthenticationError("Missing bearer token")
        settings = get_settings()
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[self._algorithm])
        except JWTError as exc:  # pragma: no cover - jose already tested
            raise AuthenticationError("Invalid token") from exc

        subject = payload.get("sub")
        username = payload.get("username") or payload.get("preferred_username")
        if subject is None or username is None:
            raise AuthenticationError("Token missing required claims")

        try:
            payload["sub"] = str(uuid.UUID(str(subject)))
        except (ValueError, TypeError) as exc:
            raise AuthenticationError("Token subject must be a UUID") from exc
        payload["username"] = username
        return payload

    def model_to_user(self, model: db.UserModel) -> User:
        return User(
            id=str(model.id),
            username=model.username,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_guest=model.is_guest,
        )


auth_service = AuthService()
