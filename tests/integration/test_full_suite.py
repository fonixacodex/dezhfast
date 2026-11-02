# tests/integration/test_full_suite.py
"""
تست سنگین end-to-end برای Dezh Framework.

اجرا:  pytest tests/integration/test_full_suite.py -v
"""
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    UnauthorizedError,
)
from app.core.security import (
    check_password,
    create_access_token,
    create_refresh_token,
    hash_password,
    read_token,
)
from app.main import app
from framework.container import Container, ContainerError


# ============================================================
# Fixtures
# ============================================================
@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@gmail.com"


# ============================================================
# 1. Security primitives
# ============================================================
class TestSecurity:
    def test_password_hash_round_trip(self):
        h = hash_password("secret123")
        assert h != "secret123"
        assert check_password("secret123", h) is True
        assert check_password("wrong", h) is False

    def test_access_token_contains_claims(self):
        token = create_access_token(user_id=42, role="user")
        payload = read_token(token)
        assert payload is not None
        assert str(payload.get("sub")) == "42" or payload.get("user_id") == 42
        assert payload.get("type") == "access"

    def test_refresh_token_contains_claims(self):
        token = create_refresh_token(user_id=42)
        payload = read_token(token)
        assert payload is not None
        assert str(payload.get("sub")) == "42" or payload.get("user_id") == 42
        assert payload.get("type") == "refresh"

    def test_invalid_token_returns_none(self):
        assert read_token("garbage.token.here") is None
        assert read_token("") is None


# ============================================================
# 2. Container (framework)
# ============================================================
class TestContainer:
    def test_bind_new_instance(self):
        c = Container()
        c.bind("x", lambda _c: object())
        assert c.resolve("x") is not c.resolve("x")

    def test_singleton_same_instance(self):
        c = Container()
        c.singleton("x", lambda _c: object())
        assert c.resolve("x") is c.resolve("x")

    def test_instance_ready_made(self):
        c = Container()
        obj = object()
        c.instance("x", obj)
        assert c.resolve("x") is obj

    def test_unknown_key(self):
        c = Container()
        with pytest.raises(ContainerError):
            c.resolve("nope")

    def test_cycle_detection(self):
        c = Container()
        c.bind("a", lambda cc: cc.resolve("b"))
        c.bind("b", lambda cc: cc.resolve("a"))
        with pytest.raises(ContainerError, match="چرخه"):
            c.resolve("a")

    def test_factory_without_container(self):
        c = Container()
        c.bind("x", lambda: 42)
        assert c.resolve("x") == 42

    def test_reset_clears_singletons(self):
        c = Container()
        count = {"n": 0}

        def factory(_c):
            count["n"] += 1
            return count["n"]

        c.singleton("x", factory)
        assert c.resolve("x") == 1
        c.reset()
        assert c.resolve("x") == 2


# ============================================================
# 3. Exceptions (direct)
# ============================================================
class TestExceptions:
    def test_not_found_code(self):
        exc = NotFoundError("پست پیدا نشد")
        assert exc.status_code == 404
        assert exc.code == "not_found"

    def test_conflict_code(self):
        exc = ConflictError("تکراری")
        assert exc.status_code == 409
        assert exc.code == "conflict"

    def test_unauthorized_code(self):
        exc = UnauthorizedError()
        assert exc.status_code == 401
        assert exc.code == "unauthorized"


# ============================================================
# 4. Health & Ready
# ============================================================
class TestHealth:
    async def test_health(self, client):
        r = await client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert body["app"] == settings.APP_NAME

    async def test_ready(self, client):
        r = await client.get("/ready")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ready"
        assert body["db"] == "ok"


# ============================================================
# 5. Request ID
# ============================================================
class TestRequestID:
    async def test_header_present(self, client):
        r = await client.get("/health")
        assert "x-request-id" in {k.lower() for k in r.headers}
        rid = r.headers.get("x-request-id")
        assert rid and len(rid) >= 6

    async def test_custom_id_echoed(self, client):
        custom = "my-custom-id-123"
        r = await client.get("/health", headers={"X-Request-ID": custom})
        assert r.headers["x-request-id"] == custom

    async def test_id_in_error_response(self, client):
        r = await client.get("/nonexistent-route-xyz")
        if "error" in r.text:
            body = r.json()
            assert "request_id" in body.get("error", {})


# ============================================================
# 6. Auth flow (end-to-end)
# ============================================================
class TestAuthFlow:
    async def test_register_login_me(self, client, unique_email):
        r = await client.post("/auth/register", json={
            "name": "Test User",
            "email": unique_email,
            "password": "secret123",
        })
        assert r.status_code == 201, r.text
        user = r.json()
        assert user["email"] == unique_email
        assert "id" in user

        r = await client.post("/auth/login", json={
            "email": unique_email,
            "password": "secret123",
        })
        assert r.status_code == 200, r.text
        tokens = r.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens

        r = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert r.status_code == 200
        assert r.json()["email"] == unique_email

    async def test_register_duplicate_email(self, client, unique_email):
        payload = {"name": "Ali", "email": unique_email, "password": "secret123"}
        r1 = await client.post("/auth/register", json=payload)
        assert r1.status_code == 201, r1.text

        r2 = await client.post("/auth/register", json=payload)
        assert r2.status_code == 409
        code = r2.json()["error"]["code"]
        assert code in ("conflict", "http_409"), f"got {code}"

    async def test_login_wrong_password(self, client, unique_email):
        await client.post("/auth/register", json={
            "name": "Ali", "email": unique_email, "password": "secret123",
        })
        r = await client.post("/auth/login", json={
            "email": unique_email, "password": "WRONG",
        })
        assert r.status_code == 401
        code = r.json()["error"]["code"]
        assert code in ("unauthorized", "invalid_token", "http_401")

    async def test_me_without_token(self, client):
        r = await client.get("/auth/me")
        assert r.status_code in (401, 403)

    async def test_refresh_token(self, client, unique_email):
        await client.post("/auth/register", json={
            "name": "Ali", "email": unique_email, "password": "secret123",
        })
        r = await client.post("/auth/login", json={
            "email": unique_email, "password": "secret123",
        })
        assert r.status_code == 200, r.text
        tokens = r.json()
        assert "refresh_token" in tokens, f"missing refresh_token: {tokens}"

        r2 = await client.post("/auth/refresh", json={
            "refresh_token": tokens["refresh_token"],
        })
        assert r2.status_code == 200
        assert "access_token" in r2.json()

    async def test_logout(self, client, unique_email):
        await client.post("/auth/register", json={
            "name": "Ali", "email": unique_email, "password": "secret123",
        })
        r = await client.post("/auth/login", json={
            "email": unique_email, "password": "secret123",
        })
        assert r.status_code == 200, r.text
        tokens = r.json()
        assert "refresh_token" in tokens, f"missing refresh_token: {tokens}"

        r2 = await client.post("/auth/logout", json={
            "refresh_token": tokens["refresh_token"],
        })
        assert r2.status_code == 200


# ============================================================
# 7. Validation
# ============================================================
class TestValidation:
    async def test_register_missing_fields(self, client):
        r = await client.post("/auth/register", json={"email": "a@b.com"})
        assert r.status_code == 422
        body = r.json()
        assert body["error"]["code"] == "validation_error"

    async def test_register_invalid_email(self, client):
        r = await client.post("/auth/register", json={
            "name": "Ali", "email": "not-an-email", "password": "secret123",
        })
        assert r.status_code == 422

    async def test_register_short_password(self, client, unique_email):
        r = await client.post("/auth/register", json={
            "name": "Ali", "email": unique_email, "password": "1",
        })
        assert r.status_code == 422


# ============================================================
# 8. Rate limiting
# ============================================================
class TestRateLimit:
    async def test_login_rate_limit(self, client, unique_email):
        await client.post("/auth/register", json={
            "name": "Ali", "email": unique_email, "password": "secret123",
        })

        statuses = []
        for _ in range(7):
            r = await client.post("/auth/login", json={
                "email": unique_email, "password": "wrong",
            })
            statuses.append(r.status_code)

        assert 429 in statuses, f"expected 429, got {statuses}"

    async def test_register_rate_limit(self, client):
        statuses = []
        for _i in range(6):
            r = await client.post("/auth/register", json={
                "name": "Ali",
                "email": f"rl_{uuid.uuid4().hex[:8]}@gmail.com",
                "password": "secret123",
            })
            statuses.append(r.status_code)

        assert 429 in statuses, f"expected 429, got {statuses}"


# ============================================================
# 9. Routes
# ============================================================
class TestRoutes:
    async def test_openapi_generates(self, client):
        r = await client.get("/openapi.json")
        assert r.status_code == 200
        spec = r.json()
        assert "paths" in spec
        assert "/auth/login" in spec["paths"]
        assert "/auth/register" in spec["paths"]

    async def test_unknown_route_404(self, client):
        r = await client.get("/this-does-not-exist-xyz")
        assert r.status_code == 404