from time import perf_counter

from fastapi import FastAPI, Request

from app.api.routes import router
from app.core.metrics import api_request_duration_seconds, api_requests_total

app = FastAPI(title='Order System API', version='0.1.0')


@app.middleware('http')
async def metrics_middleware(request: Request, call_next):
    started = perf_counter()
    response = await call_next(request)
    elapsed = perf_counter() - started

    route = request.scope.get('route')
    path_label = getattr(route, 'path', request.url.path)

    api_requests_total.labels(method=request.method, path=path_label, status=str(response.status_code)).inc()
    api_request_duration_seconds.labels(method=request.method, path=path_label).observe(elapsed)
    return response


app.include_router(router, prefix='/api/v1')
