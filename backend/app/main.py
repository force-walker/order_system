from fastapi import FastAPI, Request

from app.api.routes import router
from app.core.metrics import api_requests_total

app = FastAPI(title='Order System API', version='0.1.0')


@app.middleware('http')
async def metrics_middleware(request: Request, call_next):
    response = await call_next(request)
    route = request.scope.get('route')
    path_label = getattr(route, 'path', request.url.path)
    api_requests_total.labels(method=request.method, path=path_label, status=str(response.status_code)).inc()
    return response


app.include_router(router, prefix='/api/v1')
