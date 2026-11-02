# tests/conftest.py
"""تنظیمات مشترک تست."""
import asyncio
import contextlib
from pathlib import Path

import pytest

from app.core.config import settings
from app.core.limiter import limiter
from app.database.base import Base, import_all_models
from app.database.connection import engine


@pytest.fixture(autouse=True, scope="session")
def _setup_database():
    """ساخت پوشه و جداول دیتابیس قبل از تست‌ها (برای CI)."""
    if settings.DB_CONNECTION == "sqlite":
        db_path = Path(settings.DB_DATABASE)
        db_path.parent.mkdir(parents=True, exist_ok=True)

    import_all_models()

    async def _create():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_create())


@pytest.fixture(autouse=True)
def _reset_limiter():
    """ریست کردن rate limit بین تست‌ها."""
    with contextlib.suppress(Exception):
        limiter.reset()
    yield
    with contextlib.suppress(Exception):
        limiter.reset()