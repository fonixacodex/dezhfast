# app/modules/auth/service.py
import asyncio
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    check_password,
    create_access_token,
    create_refresh_token,
    hash_password,
    read_token,
)
from app.core.validators import is_disposable_email, is_valid_email

from .repository import AuthRepository
from .schema import UserCreate, UserLogin


class AuthService:
    def __init__(self, repo: AuthRepository):
        self.repo = repo

    # --- ثبت‌نام ---
    async def register(self, db: AsyncSession, data: UserCreate):
        email = data.email.lower()

        # ۱. چک ایمیل
        valid, msg = await asyncio.to_thread(is_valid_email, email)
        if not valid:
            raise HTTPException(400, msg)

        # ۲. چک ایمیل موقت
        if is_disposable_email(email):
            raise HTTPException(400, "ایمیل موقت قبول نیست")

        # ۳. چک تکراری
        if await self.repo.get_by_email(db, email):
            raise HTTPException(409, "این ایمیل قبلاً ثبت شده")

        # ۴. ساخت کاربر
        return await self.repo.create(
            db,
            name=data.name,
            email=email,
            password=hash_password(data.password),
            role="user",
            status="active",
            subscription_expires_at=datetime.now(UTC).replace(tzinfo=None)
            + timedelta(days=7),
        )

    # --- لاگین ---
    async def login(self, db: AsyncSession, data: UserLogin):
        email = data.email.lower()
        user = await self.repo.get_by_email(db, email)
        if not user or not check_password(data.password, user.password):
            raise HTTPException(401, "ایمیل یا پسورد اشتباهه")

        access = create_access_token(user.id, user.role)
        refresh = create_refresh_token(user.id)

        await self.repo.save_refresh_token(
            db,
            user_id=user.id,
            token=refresh,
            expires_at=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=30),
        )

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
        }

    # --- Refresh ---
    async def refresh(self, db: AsyncSession, refresh_token: str):
        payload = read_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(401, "Refresh Token نامعتبره")

        stored = await self.repo.get_refresh_token(db, refresh_token)
        if not stored:
            raise HTTPException(401, "Refresh Token باطل شده")

        try:
            user_id = int(payload["sub"])
        except (KeyError, TypeError, ValueError):
            raise HTTPException(401, "شناسه‌ی کاربر در توکن نامعتبره") from None

        stored_user = await self.repo.get_by_id(db, user_id)
        if not stored_user:
            raise HTTPException(401, "کاربر پیدا نشد")
        if stored_user.status != "active":
            raise HTTPException(403, "حساب کاربر فعال نیست")

        await self.repo.revoke_refresh_token(db, refresh_token)
        user = stored_user
        new_refresh = create_refresh_token(user.id)
        await self.repo.save_refresh_token(
            db,
            user_id=user.id,
            token=new_refresh,
            expires_at=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=30),
        )

        return {
            "access_token": create_access_token(user.id, user.role),
            "refresh_token": new_refresh,
            "token_type": "bearer",
        }

    # --- Logout ---
    async def logout(self, db: AsyncSession, refresh_token: str):
        await self.repo.revoke_refresh_token(db, refresh_token)
        return {"message": "خارج شدی"}

    # --- Logout از همه ---
    async def logout_all(self, db: AsyncSession, user_id: int):
        await self.repo.revoke_all_user_tokens(db, user_id)
        return {"message": "از همه‌ی دستگاه‌ها خارج شدی"}

    # --- ادمین: تمدید ---
    async def extend_subscription(
        self, db: AsyncSession, user_id: int, days: int = 30, note: str = ""
    ):
        user = await self.repo.get_by_id(db, user_id)
        if not user:
            raise HTTPException(404, "کاربر پیدا نشد")

        now = datetime.now(UTC).replace(tzinfo=None)
        base = max(user.subscription_expires_at or now, now)

        user.subscription_expires_at = base + timedelta(days=days)
        user.last_payment_at = now
        user.status = "active"
        if note:
            user.admin_note = note

        await db.commit()
        return {
            "message": f"اشتراک {user.email} تمدید شد",
            "expires_at": user.subscription_expires_at,
        }

    # --- ادمین: غیرفعال ---
    async def deactivate_user(
        self, db: AsyncSession, user_id: int, reason: str = ""
    ):
        user = await self.repo.get_by_id(db, user_id)
        if not user:
            raise HTTPException(404, "کاربر پیدا نشد")
        if user.role == "admin":
            raise HTTPException(403, "نمی‌تونی ادمین رو غیرفعال کنی")

        user.status = "inactive"
        if reason:
            user.admin_note = reason

        await self.repo.revoke_all_user_tokens(db, user_id)
        await db.commit()
        return {"message": f"{user.email} غیرفعال شد"}

    # --- ادمین: فعال ---
    async def activate_user(self, db: AsyncSession, user_id: int):
        user = await self.repo.get_by_id(db, user_id)
        if not user:
            raise HTTPException(404, "کاربر پیدا نشد")

        user.status = "active"
        await db.commit()
        return {"message": f"{user.email} فعال شد"}