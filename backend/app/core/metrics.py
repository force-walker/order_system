from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
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

batch_task_executions_total = Counter(
    'order_system_batch_task_executions_total',
    'Batch task execution outcomes',
    ['job_type', 'status'],
)

api_request_duration_seconds = Histogram(
    'order_system_api_request_duration_seconds',
    'API request latency in seconds',
    ['method', 'path'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)


def metrics_response() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
