# 🏰 Dezh Framework

یک فریمورک ماژولار برای FastAPI با CLI سبک Artisan.

---

## فهرست

1. [نصب](#نصب)
2. [شروع سریع](#شروع-سریع)
3. [ساختار پروژه](#ساختار-پروژه)
4. [CLI](#cli)
5. [ماژول‌ها](#ماژول‌ها)
6. [دیتابیس](#دیتابیس)
7. [Exception Handling](#exception-handling)
8. [Rate Limiting](#rate-limiting)
9. [لاگ و Request ID](#لاگ-و-request-id)
10. [Jobs (ARQ)](#jobs-arq)
11. [Docker](#docker)
12. [تست](#تست)
13. [متغیرهای محیطی](#متغیرهای-محیطی)

---

## نصب

### پیش‌نیاز

- Python 3.11+ (3.12 توصیه می‌شود)
- Redis (اختیاری، برای Jobs)
- Docker (اختیاری)

### نصب از PyPI (بعد از انتشار)

```bash
pip install dezh