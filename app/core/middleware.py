# app/core/middleware.py
"""
Middlewareها — CORS، Request ID، Request Logging.
"""
import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)


# ==================== Request ID ====================
class RequestIdMiddleware(BaseHTTPMiddleware):
    """به هر request یه ID یکتا می‌ده."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# ==================== Request Logging ====================
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """هر request رو لاگ می‌کنه — method، path، status، duration."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        request_id = getattr(request.state, "request_id", "-")

        logger.info(f"[{request_id}] → {request.method} {request.url.path}")

        try:
            response = await call_next(request)
        except Exception as exc:
            duration = (time.perf_counter() - start) * 1000
            logger.exception(
                f"[{request_id}] ✗ {request.method} {request.url.path} "
                f"— {type(exc).__name__} ({duration:.1f}ms)"
            )
            raise

        duration = (time.perf_counter() - start) * 1000
        level = logging.WARNING if response.status_code >= 400 else logging.INFO

        logger.log(
            level,
            f"[{request_id}] ← {response.status_code} "
            f"{request.method} {request.url.path} ({duration:.1f}ms)",
        )

        return response


# ==================== Register ====================
def register_middleware(app: FastAPI) -> None:
    """همه‌ی middlewareها رو ثبت کن — ترتیب add معکوس ترتیب اجراست.

    ترتیب اجرا (از بیرون به داخل):
        RequestIdMiddleware → RequestLoggingMiddleware → CORSMiddleware → route
    """

    # ۱. CORS — داخلی‌ترین (اول add می‌شود، آخر اجرا می‌شود)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_list,          # ← لیست، نه رشته
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # ۲. Request Logging — وسط
    app.add_middleware(RequestLoggingMiddleware)

    # ۳. Request ID — بیرونی‌ترین (آخر add می‌شود، اول اجرا می‌شود)
    app.add_middleware(RequestIdMiddleware)