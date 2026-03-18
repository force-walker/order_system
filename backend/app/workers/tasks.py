from datetime import UTC, datetime
import time

import redis

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.entities import BatchJobHistory
from app.workers.celery_app import celery_app

rds = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def _lock_key(order_id: int) -> str:
    return f'lock:procurement_regen:order:{order_id}'


def _update_job(task_id: str, **fields):
    db = SessionLocal()
    try:
        job = db.query(BatchJobHistory).filter(BatchJobHistory.task_id == task_id).one_or_none()
        if job is None:
            return
        for k, v in fields.items():
            setattr(job, k, v)
        db.commit()
    finally:
        db.close()


@celery_app.task(name='tasks.procurement_regeneration', bind=True)
def procurement_regeneration(self, order_id: int, requested_by: str):
    started_at = datetime.now(UTC)
    _update_job(self.request.id, status='running', started_at=started_at)

    try:
        # TODO: replace with real procurement regeneration logic
        time.sleep(2)

        finished_at = datetime.now(UTC)
        result = {
            'order_id': order_id,
            'requested_by': requested_by,
            'started_at': started_at.isoformat(),
            'finished_at': finished_at.isoformat(),
            'status': 'completed',
        }
        _update_job(
            self.request.id,
            status='completed',
            finished_at=finished_at,
            result_json=result,
            error_message=None,
        )
        return result
    except Exception as e:
        finished_at = datetime.now(UTC)
        _update_job(
            self.request.id,
            status='failed',
            finished_at=finished_at,
            error_message=str(e),
        )
        raise
    finally:
        rds.delete(_lock_key(order_id))
