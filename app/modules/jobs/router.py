# app/modules/jobs/router.py
"""endpointهای Jobs."""
from arq.connections import ArqRedis
from arq.jobs import Job, JobStatus
from fastapi import APIRouter, Depends, HTTPException

from app.modules.jobs.dependencies import get_arq_pool

router = APIRouter()


@router.post("/send-email")
async def enqueue_email(
    to: str,
    subject: str,
    body: str,
    arq: ArqRedis = Depends(get_arq_pool),
):
    """ایمیل را در پس‌زمینه بفرست."""
    job = await arq.enqueue_job("send_email", to, subject, body)
    return {"job_id": job.job_id, "status": "queued"}


@router.get("/{job_id}")
async def get_job_status(
    job_id: str,
    arq: ArqRedis = Depends(get_arq_pool),
):
    """وضعیت یک job را بگیر."""
    job = Job(job_id, arq)
    status = await job.status()
    if status is None:
        raise HTTPException(status_code=404, detail="job not found")
    result = await job.result() if status == JobStatus.complete else None
    return {"job_id": job_id, "status": status.value, "result": result}
