# app/core/security.py
import secrets
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd.hash(password.encode("utf-8")[:72].decode("utf-8", errors="ignore"))


def check_password(plain: str, hashed: str) -> bool:
    value = plain.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd.verify(value, hashed)


def create_access_token(user_id: int, role: str) -> str:
    """Create a short-lived access token."""
    return jwt.encode(
        {
            "sub": str(user_id),
            "role": role,
            "type": "access",
            "jti": secrets.token_urlsafe(16),
            "iat": datetime.now(UTC),
            "exp": datetime.now(UTC)
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        },
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(user_id: int) -> str:
    """Create a long-lived refresh token."""
    return jwt.encode(
        {
            "sub": str(user_id),
            "type": "refresh",
            "jti": secrets.token_urlsafe(16),
            "iat": datetime.now(UTC),
            "exp": datetime.now(UTC) + timedelta(days=30),
        },
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def read_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None