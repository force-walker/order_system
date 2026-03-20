from datetime import UTC, datetime

import redis

from app.core.config import settings
from app.core.metrics import batch_task_executions_total
from app.db.session import SessionLocal
from app.models.entities import BatchJobHistory, LineStatus, OrderItem, SupplierAllocation
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


@celery_app.task(
    name='tasks.procurement_regeneration',
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    retry_kwargs={'max_retries': 3},
)
def procurement_regeneration(self, order_id: int, requested_by: str):
    started_at = datetime.now(UTC)
    _update_job(self.request.id, status='running', started_at=started_at)

    db = SessionLocal()
    try:
        lines = (
            db.query(OrderItem)
            .filter(
                OrderItem.order_id == order_id,
                OrderItem.line_status.in_([LineStatus.open, LineStatus.allocated]),
            )
            .all()
        )

        created_allocations = 0
        updated_allocations = 0
        touched_lines = 0

        for line in lines:
            alloc = db.query(SupplierAllocation).filter(SupplierAllocation.order_item_id == line.id).one_or_none()
            if alloc is None:
                alloc = SupplierAllocation(
                    order_item_id=line.id,
                    suggested_qty=line.ordered_qty,
                    suggested_uom=line.order_uom_type.value,
                    final_qty=line.ordered_qty,
                    final_uom=line.order_uom_type.value,
                )
                db.add(alloc)
                created_allocations += 1
            else:
                alloc.suggested_qty = line.ordered_qty
                alloc.suggested_uom = line.order_uom_type.value
                updated_allocations += 1

            touched_lines += 1

        db.commit()

        finished_at = datetime.now(UTC)
        result = {
            'order_id': order_id,
            'requested_by': requested_by,
            'started_at': started_at.isoformat(),
            'finished_at': finished_at.isoformat(),
            'status': 'completed',
            'touched_lines': touched_lines,
            'created_allocations': created_allocations,
            'updated_allocations': updated_allocations,
            'retry_count': int(self.request.retries or 0),
        }
        _update_job(
            self.request.id,
            status='completed',
            finished_at=finished_at,
            result_json=result,
            error_message=None,
            retry_count=int(self.request.retries or 0),
            max_retries=int(self.max_retries or 3),
        )
        batch_task_executions_total.labels(job_type='procurement_regeneration', status='completed').inc()
        rds.delete(_lock_key(order_id))
        return result
    except Exception as e:
        db.rollback()
        finished_at = datetime.now(UTC)
        is_final_failure = int(self.request.retries or 0) >= int(self.max_retries or 3)
        _update_job(
            self.request.id,
            status='failed' if is_final_failure else 'retrying',
            finished_at=finished_at,
            error_message=str(e),
            retry_count=int(self.request.retries or 0),
            max_retries=int(self.max_retries or 3),
        )
        batch_task_executions_total.labels(
            job_type='procurement_regeneration',
            status='failed' if is_final_failure else 'retrying',
        ).inc()
        if is_final_failure:
            rds.delete(_lock_key(order_id))
        raise
    finally:
        db.close()
