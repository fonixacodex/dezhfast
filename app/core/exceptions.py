# app/core/exceptions.py
"""
Exceptionهای سفارشی پروژه.
"""
from typing import Any


class AppException(Exception):
    """پایه‌ی همه‌ی exceptionهای پروژه."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        code: str | None = None,
        details: Any | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.code = code or "app_error"
        self.details = details
        super().__init__(message)


# ==================== 400 ====================
class BadRequestError(AppException):
    def __init__(self, message: str = "درخواست نامعتبر", **kwargs):
        super().__init__(message, status_code=400, code="bad_request", **kwargs)


class ValidationError(AppException):
    def __init__(self, message: str = "داده‌های ورودی نامعتبر", **kwargs):
        super().__init__(message, status_code=422, code="validation_error", **kwargs)


# ==================== 401 ====================
class UnauthorizedError(AppException):
    def __init__(self, message: str = "احراز هویت لازم است", **kwargs):
        super().__init__(message, status_code=401, code="unauthorized", **kwargs)


class InvalidTokenError(AppException):
    def __init__(self, message: str = "توکن نامعتبر یا منقضی", **kwargs):
        super().__init__(message, status_code=401, code="invalid_token", **kwargs)


# ==================== 402 ====================
class SubscriptionExpiredError(AppException):
    def __init__(self, message: str = "اشتراک منقضی شده", **kwargs):
        super().__init__(message, status_code=402, code="subscription_expired", **kwargs)


# ==================== 403 ====================
class ForbiddenError(AppException):
    def __init__(self, message: str = "دسترسی مجاز نیست", **kwargs):
        super().__init__(message, status_code=403, code="forbidden", **kwargs)


class AdminRequiredError(AppException):
    def __init__(self, message: str = "فقط ادمین دسترسی دارد", **kwargs):
        super().__init__(message, status_code=403, code="admin_required", **kwargs)


# ==================== 404 ====================
class NotFoundError(AppException):
    def __init__(self, message: str = "یافت نشد", **kwargs):
        super().__init__(message, status_code=404, code="not_found", **kwargs)


# ==================== 409 ====================
class ConflictError(AppException):
    def __init__(self, message: str = "تضاد در داده", **kwargs):
        super().__init__(message, status_code=409, code="conflict", **kwargs)


# ==================== 429 ====================
class RateLimitError(AppException):
    def __init__(self, message: str = "تعداد درخواست زیاد", **kwargs):
        super().__init__(message, status_code=429, code="rate_limit", **kwargs)


# ==================== 500 ====================
class InternalError(AppException):
    def __init__(self, message: str = "خطای داخلی سرور", **kwargs):
        super().__init__(message, status_code=500, code="internal_error", **kwargs)