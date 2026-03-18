from celery import Celery

from app.core.config import settings

celery_app = Celery(
    'order_system',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Hong_Kong',
    enable_utc=False,
)
