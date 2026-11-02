# tests/unit/test_framework.py
import pytest
from fastapi import APIRouter

from framework.application import Application
from framework.container import Container, ContainerError
from framework.module import BaseModule


# ---------- Helper: پیمایش درخت routeها (سازگار با FastAPI >= 0.137) ----------
def _collect_paths(routes, prefix=""):
    """به صورت بازگشتی همه‌ی pathها را از درخت routeها جمع می‌کند."""
    paths = []
    for route in routes:
        original_router = getattr(route, "original_router", None)
        if original_router is not None:
            # _IncludedRouter: به زیرمجموعه‌ها برو و prefix را جمع کن
            include_context = getattr(route, "include_context", None)
            include_prefix = getattr(include_context, "prefix", "") or ""
            paths.extend(_collect_paths(original_router.routes, prefix + include_prefix))
        else:
            # APIRoute عادی
            path = getattr(route, "path", None)
            if path is not None:
                paths.append(prefix + path)
    return paths


# ---------- Container ----------
def test_container_bind_creates_new_instance():
    c = Container()
    c.bind("x", lambda _c: object())
    a = c.resolve("x")
    b = c.resolve("x")
    assert a is not b


def test_container_singleton_returns_same():
    c = Container()
    c.singleton("x", lambda _c: object())
    assert c.resolve("x") is c.resolve("x")


def test_container_singleton_none_is_cached():
    c = Container()
    count = {"n": 0}

    def factory(_c):
        count["n"] += 1
        return None

    c.singleton("x", factory)
    c.resolve("x")
    c.resolve("x")
    assert count["n"] == 1


def test_container_unknown_key_raises():
    c = Container()
    with pytest.raises(ContainerError):
        c.resolve("nope")


def test_container_detects_cycle():
    c = Container()
    c.bind("a", lambda cc: cc.resolve("b"))
    c.bind("b", lambda cc: cc.resolve("a"))
    with pytest.raises(ContainerError, match="چرخه"):
        c.resolve("a")


def test_container_factory_without_container_param():
    c = Container()
    c.bind("x", lambda: 42)
    assert c.resolve("x") == 42


# ---------- Application ----------
class _TestModule(BaseModule):
    name = "test"

    def register_di(self, container):
        container.singleton("svc", lambda _c: "service-instance")

    def register_routes(self, app):
        r = APIRouter()

        @r.get("/hello")
        async def hello():
            return {"ok": True}

        app.include_router(r)


def test_application_boot_and_container():
    app = Application(title="Test")
    app.register_module(_TestModule())
    fastapi_app = app.boot()

    assert app.container.resolve("svc") == "service-instance"
    
    # ✅ استفاده از helper به جای دسترسی مستقیم به .path
    paths = _collect_paths(fastapi_app.routes)
    assert "/hello" in paths


def test_application_boot_twice_raises():
    app = Application()
    app.boot()
    with pytest.raises(RuntimeError):
        app.boot()


def test_application_register_after_boot_raises():
    app = Application()
    app.boot()
    with pytest.raises(RuntimeError):
        app.register_module(_TestModule())