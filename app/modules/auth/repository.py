# app/modules/auth/repository.py
import hashlib
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import RefreshToken, User


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthRepository:
    """فقط با دیتابیس کار می‌کنه."""

    async def get_all(self, db: AsyncSession) -> list[User]:
        """همه‌ی کاربرا."""
        result = await db.execute(select(User))
        return list(result.scalars().all())

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """کاربر رو با ایمیل پیدا کن."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, user_id: int) -> User | None:
        """کاربر رو با ID پیدا کن."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        name: str,
        email: str,
        password: str,
        role: str = "user",
        status: str = "active",
        subscription_expires_at: datetime | None = None,
    ) -> User:
        user = User(
            name=name,
            email=email,
            password=password,
            role=role,
            status=status,
            subscription_expires_at=subscription_expires_at,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    # ============================
    # Refresh Token
    # ============================
    async def save_refresh_token(
        self,
        db: AsyncSession,
        user_id: int,
        token: str,
        expires_at: datetime,
    ) -> RefreshToken:
        """ذخیره‌ی refresh token توی دیتابیس."""
        rt = RefreshToken(
            user_id=user_id,
            token=_token_hash(token),
            expires_at=expires_at,
        )
        db.add(rt)
        await db.commit()
        await db.refresh(rt)
        return rt

    async def get_refresh_token(
        self, db: AsyncSession, token: str
    ) -> RefreshToken | None:
        """یه refresh token رو پیدا کن (اگه باطل نشده باشه)."""
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token == _token_hash(token),
                RefreshToken.revoked == False,  # noqa: E712
                RefreshToken.expires_at > datetime.now(UTC).replace(tzinfo=None),
            )
        )
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, db: AsyncSession, token: str) -> None:
        """باطل کردن یه refresh token (برای logout)."""
        rt = await self.get_refresh_token(db, token)
        if rt:
            rt.revoked = True
            await db.commit()

    async def revoke_all_user_tokens(self, db: AsyncSession, user_id: int) -> None:
        """باطل کردن همه‌ی refresh tokenهای یه کاربر (logout from all)."""
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False,  # noqa: E712
            )
        )
        for rt in result.scalars().all():
            rt.revoked = True
        await db.commit()