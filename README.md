# order_system

MVP bootstrap for order input / allocation / invoice workflow.

## Current status

- ✅ Draft specs in `docs/`
- ✅ Backend skeleton (FastAPI + SQLAlchemy + Alembic) in `backend/`
- ✅ Initial schema migration for dual-UOM + catch-weight model
- 🚧 API endpoints and UI screens to be implemented next

## Next tasks

1. Add order entry APIs (`orders`, `order_items`)
2. Add allocation APIs (`run-auto`, `manual-override`, `confirm`)
3. Add invoice calc/finalization API with hard-stop validation
4. Scaffold Next.js frontend and implement review screens
