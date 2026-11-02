# app/core/handlers.py
import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


def _rid(request: Request) -> str:
    return getattr(request.state, "request_id", "-")


def _error_response(status_code, message, code="error", details=None, request_id=None):
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message,
                           "details": details, "request_id": request_id}},
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.warning(
        "AppException: %s - %s (%s)",
        exc.code, exc.message, exc.status_code,
        extra={"request_id": _rid(request)},
    )
    return _error_response(exc.status_code, exc.message, exc.code, exc.details, _rid(request))


async def validation_exception_handler(request, exc) -> JSONResponse:
    errors = exc.errors()
    clean = [
        {"field": ".".join(str(loc) for loc in e.get("loc", [])),
         "message": e.get("msg", ""), "type": e.get("type", "")}
        for e in errors
    ]
    logger.warning(
        "ValidationError: %d error(s)", len(clean),
        extra={"request_id": _rid(request)},
    )
    return _error_response(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "داده‌های ورودی نامعتبر", "validation_error", clean, _rid(request),
    )


async def rate_limit_handler(request, exc: RateLimitExceeded) -> JSONResponse:
    logger.warning(
        "RateLimit: %s", exc.detail,
        extra={"request_id": _rid(request)},
    )
    return _error_response(
        status.HTTP_429_TOO_MANY_REQUESTS,
        "تعداد درخواست‌ها زیاد است. کمی صبر کن", "rate_limit",
        {"limit": str(exc.detail)}, _rid(request),
    )


async def integrity_error_handler(request, exc: IntegrityError) -> JSONResponse:
    logger.error(
        "IntegrityError: %s", exc.orig,
        extra={"request_id": _rid(request)},
    )
    msg, orig = "خطا در ذخیره‌سازی داده", str(exc.orig).lower()
    if "unique" in orig or "duplicate" in orig:
        msg = "این داده قبلاً وجود دارد"
    elif "foreign key" in orig:
        msg = "ارجاع نامعتبر به داده‌ی دیگر"
    return _error_response(
        status.HTTP_409_CONFLICT, msg, "integrity_error", None, _rid(request),
    )


async def sqlalchemy_error_handler(request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception(
        "SQLAlchemyError: %s", exc,
        extra={"request_id": _rid(request)},
    )
    return _error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "خطای دیتابیس", "database_error", None, _rid(request),
    )


async def http_exception_handler(request, exc: HTTPException) -> JSONResponse:
    return _error_response(
        exc.status_code,
        exc.detail if isinstance(exc.detail, str) else "خطا",
        f"http_{exc.status_code}",
        exc.detail if not isinstance(exc.detail, str) else None,
        _rid(request),
    )


async def general_exception_handler(request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled: %s: %s", type(exc).__name__, exc,
        extra={"request_id": _rid(request)},
    )
    return _error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "خطای داخلی سرور", "internal_error", None, _rid(request),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(PydanticValidationError, validation_exception_handler)
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)