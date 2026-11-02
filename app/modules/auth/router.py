from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_admin
from app.core.limiter import limiter
from app.database import get_db

from .repository import AuthRepository
from .schema import (
    DeactivateUser,
    ExtendSubscription,
    RefreshRequest,
    TokenResponse,
    UserAdminResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from .service import AuthService

router = APIRouter()


def get_service() -> AuthService:
    return AuthService(AuthRepository())


# ============================
# ثبت‌نام
# ============================
@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("3/minute")
async def register(
    request: Request,
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(get_service),
):
    return await service.register(db, data)


# ============================
# لاگین
# ============================
@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(get_service),
):
    return await service.login(db, data)


# ============================
# Refresh
# ============================
@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(get_service),
):
    return await service.refresh(db, data.refresh_token)


# ============================
# Logout
# ============================
@router.post("/logout")
async def logout(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(get_service),
):
    return await service.logout(db, data.refresh_token)


# ============================
# Logout از همه دستگاه‌ها
# ============================
@router.post("/logout-all")
async def logout_all(
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(get_service),
    user=Depends(get_current_user),
):
    return await service.logout_all(db, user.id)


# ============================
# پروفایل خودم
# ============================
@router.get("/me", response_model=UserResponse)
async def me(user=Depends(get_current_user)):
    return user


# ============================
# فقط ادمین (تست)
# ============================
@router.get("/admin-only")
async def admin_only(user=Depends(require_admin)):
    return {"message": f"سلام ادمین {user.name}!"}


# ============================
# ادمین: لیست کاربرا
# ============================
@router.get("/admin/users", response_model=list[UserAdminResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    repo = AuthRepository()
    return await repo.get_all(db)


# ============================
# ادمین: تمدید اشتراک
# ============================
@router.post("/admin/users/{user_id}/extend")
async def extend_subscription(
    user_id: int,
    data: ExtendSubscription,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(get_service),
    admin=Depends(require_admin),
):
    return await service.extend_subscription(db, user_id, data.days, data.note)


# ============================
# ادمین: غیرفعال کردن
# ============================
@router.post("/admin/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    data: DeactivateUser,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(get_service),
    admin=Depends(require_admin),
):
    return await service.deactivate_user(db, user_id, data.reason)


# ============================
# ادمین: فعال کردن
# ============================
@router.post("/admin/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(get_service),
    admin=Depends(require_admin),
):
    return await service.activate_user(db, user_id)