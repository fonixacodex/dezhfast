from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")

    # --- وضعیت ---
    status: Mapped[str] = mapped_column(String(20), default="active")
    # active    → فعال
    # expired   → منقضی (پول نداده)
    # inactive  → ادمین غیرفعال کرده

    # --- اشتراک ---
    subscription_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    last_payment_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    # --- یادداشت ادمین ---
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    token: Mapped[str] = mapped_column(Text, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    revoked: Mapped[bool] = mapped_column(default=False)