# app/modules/jobs/tasks.py
"""تعریف taskهای پس‌زمینه."""
import logging

logger = logging.getLogger(__name__)


async def send_email(ctx: dict, to: str, subject: str, body: str) -> dict:
    """ارسال ایمیل در پس‌زمینه (نمونه)."""
    logger.info("Sending email to %s: %s", to, subject)
    return {"status": "sent", "to": to}


async def process_report(ctx: dict, report_id: str) -> dict:
    """پردازش گزارش (نمونه)."""
    logger.info("Processing report %s", report_id)
    return {"report_id": report_id, "status": "done"}
