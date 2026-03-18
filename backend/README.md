# backend

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run API

```bash
uvicorn app.main:app --reload --port 8000
```

## Run batch worker (Celery)

```bash
celery -A app.workers.celery_app.celery_app worker --loglevel=info
```

Requires Redis and `.env` settings:
- `REDIS_URL`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`

## Run migration

```bash
alembic upgrade head
```

### Migration order (reference)

Current head chain:

1. `2026031704` (audit indexes)
2. `2026031801` (invoice lock fields)
3. `2026031802` (optimistic lock version columns)
4. `2026031803` (purchase_results.version)

If you need to verify locally:

```bash
alembic current
alembic heads
```

## Seed sample data

```bash
python scripts/seed_sample.py
```

## Run tests

```bash
pip install -r requirements-dev.txt
pytest
```

## P0 verification checklist

### 1) Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
cp .env.example .env
```

Set at minimum in `.env`:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/order_system
JWT_SECRET=change-me-in-prod
JWT_ALGORITHM=HS256
JWT_ACCESS_TTL_SECONDS=3600
JWT_REFRESH_TTL_SECONDS=1209600
```

### 2) DB / migration

```bash
alembic upgrade head
alembic current
```

### 3) Auth API smoke

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H 'content-type: application/json' \
  -d '{"user_id":"dev-admin","role":"admin"}'
```

Expect: `access_token`, `refresh_token`.

### 4) Contract smoke tests

```bash
pytest -q tests/test_openapi_contract.py
```

### 5) Existing unit tests

```bash
pytest -q
```
