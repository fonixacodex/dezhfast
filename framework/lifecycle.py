# framework/lifecycle.py
"""مدیریت startup/shutdown hookها."""

import logging
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any

logger = logging.getLogger(__name__)


Hook = Callable[[], Awaitable[None]]


class Lifecycle:
    def __init__(self) -> None:
        self.startups: list[Hook] = []
        self.shutdowns: list[Hook] = []

    def add_startup(self, hook: Hook) -> None:
        self.startups.append(hook)

    def add_shutdown(self, hook: Hook) -> None:
        self.shutdowns.append(hook)

    @asynccontextmanager
    async def lifespan(self, app: Any):
        # ---------- startup ----------
        logger.info("▶ application starting (%d hook(s))", len(self.startups))
        for hook in self.startups:
            name = getattr(hook, "__qualname__", repr(hook))
            try:
                await hook()
                logger.debug("  ✓ startup: %s", name)
            except Exception:
                logger.exception("  ✗ startup failed: %s", name)
                # تصمیم: در prod شاید بخواهی raise کنی تا اپ بالا نیاید
                # فعلاً لاگ می‌کنیم و ادامه می‌دهیم

        logger.info("✅ application started")
        try:
            yield
        finally:
            # ---------- shutdown ----------
            logger.info("⏹ application shutting down (%d hook(s))", len(self.shutdowns))
            for hook in reversed(self.shutdowns):
                name = getattr(hook, "__qualname__", repr(hook))
                try:
                    await hook()
                    logger.debug("  ✓ shutdown: %s", name)
                except Exception:
                    logger.exception("  ✗ shutdown failed: %s", name)
            logger.info("✅ application stopped")