# app/modules/jobs/worker.py
"""WorkerSettings برای ARQ worker."""
from arq.connections import RedisSettings

from app.modules.jobs.tasks import process_report, send_email


class WorkerSettings:
    functions = [send_email, process_report]
    redis_settings = RedisSettings(host="localhost", port=6379)
    max_jobs = 10
    job_timeout = 300
    keep_result = 3600
    retry_jobs = True
