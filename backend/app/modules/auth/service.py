import hashlib
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_verification_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import OAuthAccount, RefreshToken, User, UserPreference


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, email: str, password: str, full_name: str) -> tuple[User, str, str]:
        existing = await self.db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            raise ConflictException("Email already registered")

        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
        )
        self.db.add(user)
        await self.db.flush()

        prefs = UserPreference(user_id=user.id)
        self.db.add(prefs)
        await self.db.flush()

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = await self._create_refresh_token(user.id)

        import asyncio
        from app.services.analytics_service import get_analytics
        from app.services.email_service import get_email_service

        analytics = get_analytics()
        asyncio.ensure_future(analytics.track_signup(user.id, method="email"))

        email_svc = get_email_service()
        asyncio.ensure_future(email_svc.send_welcome(email, full_name))
        verification_token = create_verification_token(str(user.id))
        asyncio.ensure_future(email_svc.send_verification(email, verification_token))

        return user, access_token, refresh_token

    async def login(self, email: str, password: str) -> tuple[User, str, str]:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not user.password_hash:
            raise UnauthorizedException(message="Invalid email or password")
        if not verify_password(password, user.password_hash):
            raise UnauthorizedException(message="Invalid email or password")
        if not user.is_active:
            raise UnauthorizedException(code="AUTH_USER_INACTIVE", message="Account is deactivated")

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = await self._create_refresh_token(user.id)

        import asyncio
        from app.services.analytics_service import get_analytics

        analytics = get_analytics()
        asyncio.ensure_future(analytics.track_login(user.id, method="email"))

        return user, access_token, refresh_token

    async def google_auth(self, id_token: str) -> tuple[User, str, str]:
        import httpx
        from app.config import get_settings

        settings = get_settings()

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
            )
            if resp.status_code != 200:
                raise UnauthorizedException(message="Invalid Google token")

            google_data = resp.json()
            google_id = google_data["sub"]
            email = google_data["email"]
            full_name = google_data.get("name", email.split("@")[0])
            avatar_url = google_data.get("picture")

        if settings.google_client_id and google_data.get("aud") != settings.google_client_id:
            raise UnauthorizedException(message="Token not issued for this application")

        oauth_result = await self.db.execute(
            select(OAuthAccount).where(
                OAuthAccount.provider == "google",
                OAuthAccount.provider_id == google_id,
            )
        )
        oauth_account = oauth_result.scalar_one_or_none()

        if oauth_account:
            user_result = await self.db.execute(
                select(User).where(User.id == oauth_account.user_id)
            )
            user = user_result.scalar_one_or_none()
            if not user or not user.is_active:
                raise UnauthorizedException(code="AUTH_USER_INACTIVE", message="Account is deactivated")
        else:
            existing_user = await self.db.execute(select(User).where(User.email == email))
            user = existing_user.scalar_one_or_none()

            if user:
                oauth_account = OAuthAccount(user_id=user.id, provider="google", provider_id=google_id)
                self.db.add(oauth_account)
            else:
                user = User(
                    email=email,
                    full_name=full_name,
                    avatar_url=avatar_url,
                )
                self.db.add(user)
                await self.db.flush()

                prefs = UserPreference(user_id=user.id)
                self.db.add(prefs)

                oauth_account = OAuthAccount(user_id=user.id, provider="google", provider_id=google_id)
                self.db.add(oauth_account)

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = await self._create_refresh_token(user.id)

        import asyncio
        from app.services.analytics_service import get_analytics

        analytics = get_analytics()
        asyncio.ensure_future(analytics.track_signup(user.id, method="google"))
        asyncio.ensure_future(analytics.track_login(user.id, method="google"))

        return user, access_token, refresh_token

    async def refresh(self, refresh_token_str: str) -> tuple[str, str]:
        payload = decode_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException(code="AUTH_TOKEN_INVALID", message="Invalid refresh token")

        token_hash = hashlib.sha256(refresh_token_str.encode()).hexdigest()
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        stored = result.scalar_one_or_none()

        if not stored:
            raise UnauthorizedException(code="AUTH_TOKEN_INVALID", message="Refresh token has been revoked")

        user_id = uuid.UUID(payload["sub"])
        new_access = create_access_token({"sub": str(user_id)})
        new_refresh = await self._create_refresh_token(user_id)

        await self.db.delete(stored)

        return new_access, new_refresh

    async def logout(self, refresh_token_str: str) -> None:
        token_hash = hashlib.sha256(refresh_token_str.encode()).hexdigest()
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        stored = result.scalar_one_or_none()
        if stored:
            await self.db.delete(stored)

    async def forgot_password(self, email: str) -> None:
        from app.services.email_service import get_email_service

        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            return

        from datetime import timedelta

        reset_token = create_access_token({"sub": str(user.id), "purpose": "password_reset"}, expires_delta=timedelta(hours=1))

        email_svc = get_email_service()
        import asyncio
        asyncio.ensure_future(email_svc.send_password_reset(email, reset_token))

    async def reset_password(self, token: str, new_password: str) -> None:
        payload = decode_token(token)
        if not payload or payload.get("purpose") != "password_reset":
            raise UnauthorizedException(code="AUTH_TOKEN_INVALID", message="Invalid or expired reset token")

        user_id = uuid.UUID(payload["sub"])
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise UnauthorizedException(code="AUTH_USER_INACTIVE", message="Account not found or deactivated")

        user.password_hash = hash_password(new_password)
        await self.db.flush()

        from sqlalchemy import delete
        await self.db.execute(
            delete(RefreshToken).where(RefreshToken.user_id == user_id)
        )

    async def verify_email(self, token: str) -> None:
        payload = decode_token(token)
        if not payload or payload.get("purpose") != "email_verification":
            raise UnauthorizedException(code="AUTH_TOKEN_INVALID", message="Invalid or expired verification token")

        user_id = uuid.UUID(payload["sub"])
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException("User")

        user.is_email_verified = True
        await self.db.flush()

    async def resend_verification(self, email: str) -> None:
        from app.services.email_service import get_email_service

        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user or user.is_email_verified:
            return

        verification_token = create_verification_token(str(user.id))
        email_svc = get_email_service()
        import asyncio
        asyncio.ensure_future(email_svc.send_verification(email, verification_token))

    async def _create_refresh_token(self, user_id: uuid.UUID) -> str:
        from datetime import timedelta

        token = create_refresh_token({"sub": str(user_id)})
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        from datetime import datetime, timezone

        rt = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        self.db.add(rt)
        await self.db.flush()

        return token
