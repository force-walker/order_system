from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, require_roles
from app.core.errors import api_error
from app.db.session import get_db
from app.models.entities import PricingBasis, Product
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(prefix='/products', tags=['products'])


@router.get('', response_model=list[ProductResponse])
def list_products(
    active: bool | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'order_entry', 'buyer')),
) -> list[ProductResponse]:
    q = db.query(Product)
    if active is not None:
        q = q.filter(Product.active == active)
    rows = q.order_by(Product.id.asc()).limit(limit).all()
    return [ProductResponse(id=r.id, sku=r.sku, name=r.name, active=r.active, version=r.version) for r in rows]


@router.get('/{product_id}', response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'order_entry', 'buyer')),
) -> ProductResponse:
    product = db.query(Product).filter(Product.id == product_id).one_or_none()
    if product is None:
        api_error(404, 'RESOURCE_NOT_FOUND', 'product not found')
    return ProductResponse(id=product.id, sku=product.sku, name=product.name, active=product.active, version=product.version)


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
    return ProductResponse(id=product.id, sku=product.sku, name=product.name, active=product.active, version=product.version)


@router.patch('/{product_id}', response_model=ProductResponse)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin')),
) -> ProductResponse:
    product = db.query(Product).filter(Product.id == product_id).one_or_none()
    if product is None:
        api_error(404, 'RESOURCE_NOT_FOUND', 'product not found')
    if product.version != payload.version:
        api_error(409, 'VERSION_CONFLICT', 'record has been updated by another user')

    data = payload.model_dump(exclude_unset=True)
    data.pop('version', None)
    for key, value in data.items():
        setattr(product, key, value)

    product.version += 1
    db.commit()
    db.refresh(product)
    return ProductResponse(id=product.id, sku=product.sku, name=product.name, active=product.active, version=product.version)
