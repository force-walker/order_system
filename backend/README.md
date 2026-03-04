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

## Run migration

```bash
alembic upgrade head
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
