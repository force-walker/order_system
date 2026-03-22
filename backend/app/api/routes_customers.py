from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, require_roles
from app.core.errors import api_error
from app.db.session import get_db
from app.models.entities import Customer
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate

router = APIRouter(prefix='/customers', tags=['customers'])


@router.get('', response_model=list[CustomerResponse])
def list_customers(
    active: bool | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'order_entry', 'buyer')),
) -> list[CustomerResponse]:
    q = db.query(Customer)
    if active is not None:
        q = q.filter(Customer.active == active)
    rows = q.order_by(Customer.id.asc()).limit(limit).all()
    return [CustomerResponse(id=r.id, code=r.code, name=r.name, active=r.active, version=r.version) for r in rows]


@router.get('/{customer_id}', response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'order_entry', 'buyer')),
) -> CustomerResponse:
    row = db.query(Customer).filter(Customer.id == customer_id).one_or_none()
    if row is None:
        api_error(404, 'RESOURCE_NOT_FOUND', 'customer not found')
    return CustomerResponse(id=row.id, code=row.code, name=row.name, active=row.active, version=row.version)


@router.post('', response_model=CustomerResponse)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin')),
) -> CustomerResponse:
    row = Customer(code=payload.code, name=payload.name, active=payload.active)
    db.add(row)
    db.commit()
    db.refresh(row)
    return CustomerResponse(id=row.id, code=row.code, name=row.name, active=row.active, version=row.version)


@router.patch('/{customer_id}', response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin')),
) -> CustomerResponse:
    row = db.query(Customer).filter(Customer.id == customer_id).one_or_none()
    if row is None:
        api_error(404, 'RESOURCE_NOT_FOUND', 'customer not found')
    if row.version != payload.version:
        api_error(409, 'VERSION_CONFLICT', 'record has been updated by another user')

    data = payload.model_dump(exclude_unset=True)
    data.pop('version', None)
    for k, v in data.items():
        setattr(row, k, v)

    row.version += 1
    db.commit()
    db.refresh(row)
    return CustomerResponse(id=row.id, code=row.code, name=row.name, active=row.active, version=row.version)
