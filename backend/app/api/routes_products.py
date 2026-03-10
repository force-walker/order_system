from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, require_roles
from app.db.session import get_db
from app.models.entities import PricingBasis, Product
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter(prefix='/products', tags=['products'])


@router.post('', response_model=ProductResponse)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin')),
) -> ProductResponse:
    product = Product(
        sku=payload.sku,
        name=payload.name,
        order_uom=payload.order_uom,
        purchase_uom=payload.purchase_uom,
        invoice_uom=payload.invoice_uom,
        is_catch_weight=payload.is_catch_weight,
        weight_capture_required=payload.weight_capture_required,
        pricing_basis_default=PricingBasis(payload.pricing_basis_default),
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return ProductResponse(id=product.id, sku=product.sku, name=product.name)
