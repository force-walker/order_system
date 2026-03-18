from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


EXPECTED_PATHS = {
    '/api/v1/health',
    '/api/v1/auth/login',
    '/api/v1/auth/refresh',
    '/api/v1/auth/logout',
    '/api/v1/auth/me',
    '/api/v1/batch/procurement-regeneration',
    '/api/v1/batch/jobs/{task_id}',
    '/api/v1/products',
    '/api/v1/products/{product_id}',
    '/api/v1/customers',
    '/api/v1/customers/{customer_id}',
    '/api/v1/orders',
    '/api/v1/orders/{order_id}/bulk-transition',
    '/api/v1/allocations/run-auto',
    '/api/v1/allocations/{allocation_id}/override',
    '/api/v1/allocations/{allocation_id}/split-line',
    '/api/v1/purchase-results',
    '/api/v1/purchase-results/{result_id}',
    '/api/v1/purchase-results/bulk-upsert',
    '/api/v1/invoices',
    '/api/v1/invoices/{invoice_id}/finalize',
    '/api/v1/invoices/{invoice_id}/reset-to-draft',
    '/api/v1/invoices/{invoice_id}/unlock',
}


def test_runtime_openapi_has_expected_v1_paths():
    schema = client.get('/openapi.json').json()
    runtime_paths = set(schema['paths'].keys())
    missing = EXPECTED_PATHS - runtime_paths
    assert not missing, f'missing runtime paths: {sorted(missing)}'


def test_runtime_openapi_does_not_expose_legacy_api_prefix_paths():
    schema = client.get('/openapi.json').json()
    legacy = [p for p in schema['paths'].keys() if p.startswith('/api/') and not p.startswith('/api/v1/')]
    assert not legacy, f'legacy /api/* paths detected: {legacy}'


def test_error_payload_shape_code_message():
    # no auth -> should return standardized error payload
    res = client.post('/api/v1/orders', json={})
    body = res.json()
    assert res.status_code == 401
    assert isinstance(body, dict)
    assert 'detail' in body
    assert set(body['detail'].keys()) == {'code', 'message'}
