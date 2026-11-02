# app/core/logging.py
"""
Logging setup — dev: متن رنگی، prod: JSON ساختاریافته.
"""
import json
import logging
import sys
from datetime import UTC, datetime

from app.core.config import settings


# ==================== Formatters ====================
class JSONFormatter(logging.Formatter):
    """هر خط لاگ را به یک JSON تبدیل می‌کند — مناسب production."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=UTC
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["request_id"] = request_id

        for key in ("user_id", "method", "path", "status_code", "duration_ms"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value

        if record.exc_info:
            payload["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        return json.dumps(payload, ensure_ascii=False)


class DevFormatter(logging.Formatter):
    """فرمت خوانا برای dev — با رنگ‌بندی ساده."""

    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
    }
    RESET = "\033[0m"
    DIM = "\033[2m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        ts = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        request_id = getattr(record, "request_id", None)

        rid = f"{self.DIM}[{request_id}]{self.RESET} " if request_id else ""

        base = (
            f"{self.DIM}{ts}{self.RESET} "
            f"{color}{record.levelname:<8}{self.RESET} "
            f"{self.DIM}{record.name}{self.RESET} "
            f"{rid}{record.getMessage()}"
        )

        if record.exc_info:
            base += "\n" + self.formatException(record.exc_info)

        return base


# ==================== Setup ====================
def setup_logging() -> None:
    """روی startup صدا زده می‌شود."""

    handler = logging.StreamHandler(sys.stdout)

    if settings.APP_ENV == "prod":
        handler.setFormatter(JSONFormatter())
        level = logging.INFO
    else:
        handler.setFormatter(DevFormatter())
        level = logging.DEBUG if settings.DEBUG else logging.INFO

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # پکیج‌های پرحرف را آرام کن
    logging.getLogger("passlib").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)   # ← جدید
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)

    root.info("✅ Logging setup complete (env=%s, level=%s)", settings.APP_ENV, level)