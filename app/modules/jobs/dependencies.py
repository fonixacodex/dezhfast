# app/modules/jobs/dependencies.py
"""وابستگی‌های FastAPI برای ARQ."""
from arq import create_pool
from arq.connections import ArqRedis, RedisSettings


async def get_arq_pool() -> ArqRedis:
    return await create_pool(RedisSettings(host="localhost", port=6379))
