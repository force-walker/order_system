from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import issue_tokens
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.entities import BatchJobHistory, LineStatus, Order, OrderItem, OrderStatus, PricingBasis, SupplierAllocation
from app.api import routes_batch
from app.workers import tasks


class FakeRedis:
    def __init__(self):
        self._store: dict[str, str] = {}

    def set(self, key: str, value: str, nx: bool = False, ex: int | None = None):
        if nx and key in self._store:
            return False
        self._store[key] = value
        return True

    def delete(self, key: str):
        self._store.pop(key, None)
        return 1


class _FakeAsyncTask:
    def __init__(self, task_id: str):
        self.id = task_id


class _FakeDelay:
    def __init__(self):
        self.next_id = 'task-1'

    def delay(self, *args, **kwargs):
        return _FakeAsyncTask(self.next_id)


def _auth_header(user_id: str = 'e2e-user', role: str = 'buyer') -> dict[str, str]:
    access, _, _ = issue_tokens(user_id=user_id, role=role)
    return {'Authorization': f'Bearer {access}'}


def _setup_test_env(monkeypatch):
    engine = create_engine(
        'sqlite+pysqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
        future=True,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    fake_redis = FakeRedis()
    monkeypatch.setattr(routes_batch, 'rds', fake_redis)
    monkeypatch.setattr(tasks, 'rds', fake_redis)
    monkeypatch.setattr(tasks, 'SessionLocal', TestingSessionLocal)

    delay_stub = _FakeDelay()
    monkeypatch.setattr(routes_batch, 'procurement_regeneration', delay_stub)

    db = TestingSessionLocal()
    order = Order(
        order_no='E2E-001',
        customer_id=1,
        order_datetime=datetime.utcnow(),
        delivery_date=datetime.utcnow().date(),
        delivery_type='pickup',
        status=OrderStatus.confirmed,
    )
    db.add(order)
    db.flush()
    db.add(
        OrderItem(
            order_id=order.id,
            product_id=1,
            ordered_qty=2,
            order_uom_type=PricingBasis.uom_count,
            pricing_basis=PricingBasis.uom_count,
            tax_code='standard',
            line_status=LineStatus.open,
        )
    )
    db.commit()
    db.close()

    return TestingSessionLocal, delay_stub


def test_batch_e2e_enqueue_worker_and_retry_flow(monkeypatch):
    TestingSessionLocal, delay_stub = _setup_test_env(monkeypatch)
    client = TestClient(app)

    # 1) enqueue
    res = client.post('/api/v1/batch/procurement-regeneration', json={'order_id': 1}, headers=_auth_header())
    assert res.status_code == 200
    task_id = res.json()['task_id']

    # 2) run worker logic using same task_id
    tasks.procurement_regeneration.apply(args=[1, 'e2e-user'], task_id=task_id, throw=True)

    # 3) verify history/status and allocation creation
    db = TestingSessionLocal()
    hist = db.query(BatchJobHistory).filter(BatchJobHistory.task_id == task_id).one()
    assert hist.status == 'completed'
    alloc_count = db.query(SupplierAllocation).count()
    assert alloc_count == 1

    # 4) prepare failed history and retry
    failed = BatchJobHistory(
        task_id='failed-1',
        job_type='procurement_regeneration',
        order_id=1,
        status='failed',
        requested_by='e2e-user',
        retry_count=0,
        max_retries=3,
    )
    db.add(failed)
    db.commit()
    db.close()

    delay_stub.next_id = 'retry-1'
    retry_res = client.post('/api/v1/batch/jobs/failed-1/retry', headers=_auth_header())
    assert retry_res.status_code == 200
    assert retry_res.json()['task_id'] == 'retry-1'

    # 5) completed job cannot retry
    no_retry = client.post(f'/api/v1/batch/jobs/{task_id}/retry', headers=_auth_header())
    assert no_retry.status_code == 409
    assert no_retry.json()['detail']['code'] == 'RETRY_NOT_ALLOWED'

    app.dependency_overrides.clear()



def test_batch_retry_limit_exceeded(monkeypatch):
    TestingSessionLocal, delay_stub = _setup_test_env(monkeypatch)
    client = TestClient(app)

    db = TestingSessionLocal()
    failed = BatchJobHistory(
        task_id='failed-limit',
        job_type='procurement_regeneration',
        order_id=1,
        status='failed',
        requested_by='e2e-user',
        retry_count=3,
        max_retries=3,
    )
    db.add(failed)
    db.commit()
    db.close()

    delay_stub.next_id = 'should-not-run'
    res = client.post('/api/v1/batch/jobs/failed-limit/retry', headers=_auth_header())
    assert res.status_code == 409
    assert res.json()['detail']['code'] == 'RETRY_LIMIT_EXCEEDED'

    # Ensure no child retry job was created.
    db = TestingSessionLocal()
    child = db.query(BatchJobHistory).filter(BatchJobHistory.parent_task_id == 'failed-limit').first()
    assert child is None
    db.close()

    app.dependency_overrides.clear()
