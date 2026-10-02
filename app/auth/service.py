from __future__ import annotations

import uuid
from datetime import datetime

from jose import JWTError, jwt

from app.auth.models import User
from app.config.settings import get_settings


class AuthenticationError(Exception):
    """Raised when a token cannot be validated."""


class AuthService:
    def __init__(self) -> None:
        self._algorithm = "HS256"

    async def authenticate(self, token: str) -> User:
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
            user_id = str(uuid.UUID(str(subject)))
        except (ValueError, TypeError) as exc:
            raise AuthenticationError("Token subject must be a UUID") from exc

        is_active = payload.get("is_active", True)
        is_bot = payload.get("is_bot", False)

        now = datetime.utcnow()
        return User(
            id=user_id,
            username=username,
            created_at=now,
            updated_at=now,
            is_active=is_active,
            is_bot=is_bot,
        )


auth_service = AuthService()
