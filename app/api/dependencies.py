# app/api/dependencies.py
import logging
from datetime import datetime

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import read_token
from app.database import get_db
from app.modules.auth.model import User

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    # ⚠️ import داخل تابع — به‌خاطر circular import
    from app.modules.auth.repository import AuthRepository

    payload = read_token(credentials.credentials)
    if not payload:
        logger.warning("Invalid or expired token")
        raise HTTPException(401, "توکن نامعتبر یا منقضی شده")

    if payload.get("type") != "access":
        logger.warning(f"Wrong token type: {payload.get('type')}")
        raise HTTPException(401, "نوع توکن اشتباهه")

    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        logger.warning("Invalid sub in token")
        raise HTTPException(401, "شناسه‌ی کاربر در توکن نامعتبره") from None

    repo = AuthRepository()
    user = await repo.get_by_id(db, user_id)
    if not user:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(401, "کاربر پیدا نشد")

    if user.status == "inactive":
        raise HTTPException(403, "حسابت غیرفعاله. با پشتیبانی تماس بگیر")

    if user.subscription_expires_at:
        now = datetime.utcnow()
        if user.subscription_expires_at < now:
            raise HTTPException(402, "اشتراکت تموم شده. با پشتیبانی تماس بگیر")

    return user


async def require_admin(
    user: User = Depends(get_current_user),
) -> User:
    if user.role != "admin":
        raise HTTPException(403, "فقط ادمین دسترسی داره")
    return user