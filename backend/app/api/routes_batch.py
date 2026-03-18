import redis
from celery.result import AsyncResult
from fastapi import APIRouter, Depends

from app.core.auth import AuthContext, require_roles
from app.core.config import settings
from app.core.errors import api_error
from app.schemas.batch import JobEnqueueResponse, JobStatusResponse, ProcurementRegenerationRequest
from app.workers.tasks import procurement_regeneration

router = APIRouter(prefix='/batch', tags=['batch'])
rds = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def _lock_key(order_id: int) -> str:
    return f'lock:procurement_regen:order:{order_id}'


@router.post('/procurement-regeneration', response_model=JobEnqueueResponse)
def enqueue_procurement_regeneration(
    payload: ProcurementRegenerationRequest,
    auth: AuthContext = Depends(require_roles('admin', 'buyer')),
) -> JobEnqueueResponse:
    key = _lock_key(payload.order_id)
    acquired = rds.set(key, auth.user_id, nx=True, ex=60 * 30)
    if not acquired:
        api_error(409, 'REGENERATION_IN_PROGRESS', 'procurement regeneration already running for this order')

    task = procurement_regeneration.delay(payload.order_id, auth.user_id)
    return JobEnqueueResponse(task_id=task.id, status='queued')


@router.get('/jobs/{task_id}', response_model=JobStatusResponse)
def get_job_status(
    task_id: str,
    auth: AuthContext = Depends(require_roles('admin', 'buyer', 'order_entry')),
) -> JobStatusResponse:
    res = AsyncResult(task_id)
    status = str(res.status).lower()

    result: dict | None = None
    if res.successful():
        val = res.result
        if isinstance(val, dict):
            result = val
        else:
            result = {'value': str(val)}

    return JobStatusResponse(task_id=task_id, status=status, result=result)
