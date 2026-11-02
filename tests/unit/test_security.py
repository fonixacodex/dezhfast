from datetime import UTC, datetime, timedelta

from app.core.security import (
    check_password,
    create_access_token,
    create_refresh_token,
    hash_password,
    read_token,
)


def test_password_hash_round_trip() -> None:
    password = "correct horse battery staple"
    hashed = hash_password(password)

    assert hashed != password
    assert check_password(password, hashed)
    assert not check_password("wrong password", hashed)


def test_access_token_contains_access_claims() -> None:
    token = create_access_token(7, "admin")
    payload = read_token(token)

    assert payload is not None
    assert payload["sub"] == "7"
    assert payload["role"] == "admin"
    assert payload["type"] == "access"


def test_refresh_token_contains_refresh_claims() -> None:
    token = create_refresh_token(7)
    payload = read_token(token)

    assert payload is not None
    assert payload["sub"] == "7"
    assert payload["type"] == "refresh"
    assert datetime.fromtimestamp(payload["exp"], tz=UTC) > datetime.now(
        UTC
    ) + timedelta(days=29)


def test_invalid_token_is_rejected() -> None:
    assert read_token("not-a-jwt") is None
