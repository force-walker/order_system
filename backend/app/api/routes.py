from fastapi import APIRouter

from app.api.routes_allocations import router as allocations_router
from app.api.routes_invoices import router as invoices_router
from app.api.routes_orders import router as orders_router
from app.api.routes_products import router as products_router
from app.api.routes_transitions import router as transitions_router
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get('/health', response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status='ok')


router.include_router(products_router)
router.include_router(orders_router)
router.include_router(allocations_router)
router.include_router(invoices_router)
router.include_router(transitions_router)
