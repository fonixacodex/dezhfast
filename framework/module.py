# framework/module.py
"""BaseModule — هر ماژول از این ارث می‌برد."""

import logging
from abc import ABC, abstractmethod

from framework.container import Container

logger = logging.getLogger(__name__)


class BaseModule(ABC):
    """پایه‌ی همه‌ی ماژول‌ها."""

    name: str = ""

    # ---------- چرخه ----------
    @abstractmethod
    def register_di(self, container: Container) -> None:
        """وابستگی‌های ماژول را در container ثبت کن."""

    @abstractmethod
    def register_routes(self, app) -> None:
        """روترهای ماژول را روی app ثبت کن."""

    async def on_startup(self) -> None:  # noqa: B027
        """هوک اختیاری — قبل از شروع سرو."""

    async def on_shutdown(self) -> None:  # noqa: B027
        """هوک اختیاری — هنگام خاموشی."""

    # ---------- کمکی ----------
    def __repr__(self) -> str:
        return f"<{type(self).__name__} name={self.name!r}>"