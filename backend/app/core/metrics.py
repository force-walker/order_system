from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from starlette.responses import Response

api_requests_total = Counter(
    'order_system_api_requests_total',
    'Total API requests',
    ['method', 'path', 'status'],
)

batch_enqueues_total = Counter(
    'order_system_batch_enqueues_total',
    'Batch enqueue attempts',
    ['job_type', 'result'],
)

batch_retries_total = Counter(
    'order_system_batch_retries_total',
    'Batch retry attempts',
    ['job_type', 'result'],
)


def metrics_response() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
