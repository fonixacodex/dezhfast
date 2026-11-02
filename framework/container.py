# framework/container.py
"""DI Container ساده و قابل اتکا."""

from collections.abc import Callable
from typing import Any


class ContainerError(Exception):
    """خطاهای container."""


class Container:
    """
    DI Container با پشتیبانی از bind (جدید هر بار) و singleton (کش‌شده).

    factory می‌تواند یکی از این‌ها باشد:
        - تابع بدون پارامتر:       lambda: MyService()
        - تابع با پارامتر container: lambda c: MyService(c.resolve("db"))
    """

    def __init__(self) -> None:
        self._bindings: dict[str, Callable[..., Any]] = {}
        self._singletons: dict[str, Any] = {}
        self._singleton_keys: set[str] = set()
        self._resolving: set[str] = set()  # برای detect چرخه

    # ---------- ثبت ----------
    def bind(self, key: str, factory: Callable[..., Any]) -> None:
        """هر بار resolve، نمونه‌ی جدید ساخته می‌شود."""
        if key in self._singletons:
            del self._singletons[key]
        self._singleton_keys.discard(key)
        self._bindings[key] = factory

    def singleton(self, key: str, factory: Callable[..., Any]) -> None:
        """فقط یک بار ساخته می‌شود، بعد کش می‌شود."""
        self._bindings[key] = factory
        self._singleton_keys.add(key)
        self._singletons.pop(key, None)

    def instance(self, key: str, value: Any) -> None:
        """یک نمونه‌ی آماده را به عنوان singleton ثبت کن."""
        self._bindings[key] = lambda _c: value
        self._singleton_keys.add(key)
        self._singletons[key] = value

    # ---------- حل ----------
    def resolve(self, key: str) -> Any:
        """یک وابستگی را برمی‌گرداند."""
        if key not in self._bindings:
            raise ContainerError(f"'{key}' تعریف نشده است")

        # singleton کش‌شده؟
        if key in self._singleton_keys and key in self._singletons:
            return self._singletons[key]

        # detect چرخه
        if key in self._resolving:
            chain = " → ".join([*self._resolving, key])
            raise ContainerError(f"چرخه‌ی وابستگی detected: {chain}")

        self._resolving.add(key)
        try:
            factory = self._bindings[key]
            value = self._call_factory(factory)
        finally:
            self._resolving.discard(key)

        if key in self._singleton_keys:
            self._singletons[key] = value

        return value

    def _call_factory(self, factory: Callable[..., Any]) -> Any:
        """factory را با یا بدون پارامتر container صدا بزن."""
        try:
            # امتحان می‌کنیم با container
            return factory(self)
        except TypeError:
            # اگر امضا پارامتر نمی‌گرفت، بدون پارامتر صدا بزن
            return factory()

    # ---------- کمکی ----------
    def has(self, key: str) -> bool:
        return key in self._bindings

    def reset(self) -> None:
        """پاک کردن همه‌ی singletonها (مفید در تست‌ها)."""
        self._singletons.clear()
        self._resolving.clear()