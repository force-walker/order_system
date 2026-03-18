from datetime import UTC, datetime
import time

import redis

from app.core.config import settings
from app.workers.celery_app import celery_app

rds = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def _lock_key(order_id: int) -> str:
    return f'lock:procurement_regen:order:{order_id}'


@celery_app.task(name='tasks.procurement_regeneration', bind=True)
def procurement_regeneration(self, order_id: int, requested_by: str):
    # Placeholder batch work
    started_at = datetime.now(UTC).isoformat()
    time.sleep(2)
    finished_at = datetime.now(UTC).isoformat()

    # release lock when task ends
    rds.delete(_lock_key(order_id))

    return {
        'order_id': order_id,
        'requested_by': requested_by,
        'started_at': started_at,
        'finished_at': finished_at,
        'status': 'completed',
    }
