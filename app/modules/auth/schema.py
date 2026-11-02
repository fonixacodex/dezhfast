# app/modules/auth/schema.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)          # ← جدید
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)      # ← جدید


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserAdminResponse(BaseModel):
    """خروجی برای ادمین."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: str
    status: str
    subscription_expires_at: datetime | None
    last_payment_at: datetime | None
    admin_note: str | None


class ExtendSubscription(BaseModel):
    days: int = Field(30, ge=1, le=3650)                          # ← جدید
    note: str = ""


class DeactivateUser(BaseModel):
    reason: str = ""