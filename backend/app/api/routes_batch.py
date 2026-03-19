import redis
from celery.result import AsyncResult
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, require_roles
from app.core.config import settings
from app.core.errors import api_error
from app.db.session import get_db
from app.models.entities import BatchJobHistory
from app.schemas.batch import (
    JobEnqueueResponse,
    JobHistoryItem,
    JobHistoryListResponse,
    JobStatusResponse,
    ProcurementRegenerationRequest,
)
from app.workers.tasks import procurement_regeneration

router = APIRouter(prefix='/batch', tags=['batch'])
rds = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def _lock_key(order_id: int) -> str:
    return f'lock:procurement_regen:order:{order_id}'


@router.get('/jobs', response_model=JobHistoryListResponse)
def list_jobs(
    job_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    order_id: int | None = Query(default=None, ge=1),
    from_ts: datetime | None = Query(default=None),
    to_ts: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'buyer', 'order_entry')),
) -> JobHistoryListResponse:
    q = db.query(BatchJobHistory)
    if job_type:
        q = q.filter(BatchJobHistory.job_type == job_type)
    if status:
        q = q.filter(BatchJobHistory.status == status)
    if order_id:
        q = q.filter(BatchJobHistory.order_id == order_id)
    if from_ts:
        q = q.filter(BatchJobHistory.requested_at >= from_ts)
    if to_ts:
        q = q.filter(BatchJobHistory.requested_at <= to_ts)

    rows = q.order_by(BatchJobHistory.requested_at.desc()).limit(limit).all()
    items = [
        JobHistoryItem(
            task_id=r.task_id,
            job_type=r.job_type,
            order_id=r.order_id,
            status=r.status,
            requested_by=r.requested_by,
            requested_at=r.requested_at.isoformat() if r.requested_at else '',
            started_at=r.started_at.isoformat() if r.started_at else None,
            finished_at=r.finished_at.isoformat() if r.finished_at else None,
            parent_task_id=r.parent_task_id,
            retry_count=int(r.retry_count or 0),
            max_retries=int(r.max_retries or 3),
        )
        for r in rows
    ]
    return JobHistoryListResponse(items=items, count=len(items))


@router.post('/procurement-regeneration', response_model=JobEnqueueResponse)
def enqueue_procurement_regeneration(
    payload: ProcurementRegenerationRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'buyer')),
) -> JobEnqueueResponse:
    key = _lock_key(payload.order_id)
    acquired = rds.set(key, auth.user_id, nx=True, ex=60 * 30)
    if not acquired:
        api_error(409, 'REGENERATION_IN_PROGRESS', 'procurement regeneration already running for this order')

    task = procurement_regeneration.delay(payload.order_id, auth.user_id)

    db.add(
        BatchJobHistory(
            task_id=task.id,
            job_type='procurement_regeneration',
            order_id=payload.order_id,
            status='queued',
            requested_by=auth.user_id,
        )
    )
    db.commit()

    return JobEnqueueResponse(task_id=task.id, status='queued', retry_count=0)



@router.post('/jobs/{task_id}/retry', response_model=JobEnqueueResponse)
def retry_job(
    task_id: str,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'buyer')),
) -> JobEnqueueResponse:
    history = db.query(BatchJobHistory).filter(BatchJobHistory.task_id == task_id).one_or_none()
    if history is None:
        api_error(404, 'RESOURCE_NOT_FOUND', 'batch job not found')
    if history.job_type != 'procurement_regeneration':
        api_error(422, 'INVALID_TRANSITION_PAIR', 'retry unsupported for this job type')
    if history.order_id is None:
        api_error(409, 'STATUS_NO_TARGET_LINES', 'order_id missing in history')
    if history.status != 'failed':
        api_error(409, 'RETRY_NOT_ALLOWED', 'retry allowed only for failed jobs')
    if int(history.retry_count or 0) >= int(history.max_retries or 3):
        api_error(409, 'RETRY_LIMIT_EXCEEDED', 'retry limit exceeded')

    has_child = (
        db.query(BatchJobHistory)
        .filter(BatchJobHistory.parent_task_id == history.task_id)
        .first()
        is not None
    )
    if has_child:
        api_error(409, 'RETRY_NOT_ALLOWED', 'retry only allowed on latest attempt')

    key = _lock_key(history.order_id)
    acquired = rds.set(key, auth.user_id, nx=True, ex=60 * 30)
    if not acquired:
        api_error(409, 'REGENERATION_IN_PROGRESS', 'procurement regeneration already running for this order')

    task = procurement_regeneration.delay(history.order_id, auth.user_id)

    retry_count = int(history.retry_count or 0) + 1
    db.add(
        BatchJobHistory(
            task_id=task.id,
            parent_task_id=history.task_id,
            job_type=history.job_type,
            order_id=history.order_id,
            status='queued',
            requested_by=auth.user_id,
            retry_count=retry_count,
            max_retries=history.max_retries or 3,
        )
    )
    db.commit()

    return JobEnqueueResponse(task_id=task.id, status='queued', retry_count=retry_count)

@router.get('/jobs/{task_id}', response_model=JobStatusResponse)
def get_job_status(
    task_id: str,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'buyer', 'order_entry')),
) -> JobStatusResponse:
    history = db.query(BatchJobHistory).filter(BatchJobHistory.task_id == task_id).one_or_none()

    if history is not None:
        return JobStatusResponse(
            task_id=task_id,
            status=history.status,
            result=history.result_json,
            error_message=history.error_message,
            retry_count=int(history.retry_count or 0),
            max_retries=int(history.max_retries or 3),
        )

    # fallback for older tasks created before history table was introduced
    res = AsyncResult(task_id)
    status = str(res.status).lower()

    result: dict | None = None
    if res.successful():
        val = res.result
        if isinstance(val, dict):
            result = val
        else:
            result = {'value': str(val)}

    return JobStatusResponse(task_id=task_id, status=status, result=result, error_message=None, retry_count=0, max_retries=3)
