import uuid

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token
from app.database.postgres import get_db
from app.models import User


async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization.startswith("Bearer "):
        raise UnauthorizedException(code="AUTH_TOKEN_INVALID", message="Invalid authorization header")

    token = authorization.removeprefix("Bearer ")
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        raise UnauthorizedException(code="AUTH_TOKEN_EXPIRED", message="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException(code="AUTH_TOKEN_INVALID", message="Invalid token payload")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise UnauthorizedException(code="AUTH_USER_INACTIVE", message="User not found or inactive")

    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException(message="Admin access required")
    return current_user
