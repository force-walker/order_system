from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, require_roles
from app.core.errors import api_error
from app.db.session import get_db
from app.models.entities import PurchaseResult, SupplierAllocation
from app.schemas.purchase_result import (
    PurchaseResultBulkUpsertRequest,
    PurchaseResultResponse,
    PurchaseResultUpsertRequest,
)

router = APIRouter(prefix='/purchase-results', tags=['purchase-results'])


def _apply_payload(target: PurchaseResult, payload: PurchaseResultUpsertRequest, actor: str) -> None:
    target.allocation_id = payload.allocation_id
    target.supplier_id = payload.supplier_id
    target.purchased_qty = payload.purchased_qty
    target.purchased_uom = payload.purchased_uom
    target.actual_weight_kg = payload.actual_weight_kg
    target.unit_cost = payload.unit_cost
    target.final_unit_cost = payload.final_unit_cost
    target.result_status = payload.result_status
    target.shortage_qty = payload.shortage_qty
    target.shortage_policy = payload.shortage_policy
    target.invoiceable_flag = payload.invoiceable_flag
    target.note = payload.note
    target.recorded_by = actor
    target.recorded_at = datetime.utcnow()


@router.post('', response_model=PurchaseResultResponse)
def create_purchase_result(
    payload: PurchaseResultUpsertRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'buyer', 'supplier')),
) -> PurchaseResultResponse:
    alloc = db.query(SupplierAllocation).filter(SupplierAllocation.id == payload.allocation_id).one_or_none()
    if alloc is None:
        api_error(404, 'ALLOCATION_NOT_FOUND', 'allocation not found')

    rec = PurchaseResult()
    _apply_payload(rec, payload, auth.user_id)
    rec.version = 1
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return PurchaseResultResponse(id=rec.id, allocation_id=rec.allocation_id, result_status=rec.result_status, version=rec.version)


@router.patch('/{result_id}', response_model=PurchaseResultResponse)
def update_purchase_result(
    result_id: int,
    payload: PurchaseResultUpsertRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'buyer', 'supplier')),
) -> PurchaseResultResponse:
    rec = db.query(PurchaseResult).filter(PurchaseResult.id == result_id).one_or_none()
    if rec is None:
        api_error(404, 'RESOURCE_NOT_FOUND', 'purchase result not found')
    if rec.version != payload.version:
        api_error(409, 'VERSION_CONFLICT', 'record has been updated by another user')

    alloc = db.query(SupplierAllocation).filter(SupplierAllocation.id == payload.allocation_id).one_or_none()
    if alloc is None:
        api_error(404, 'ALLOCATION_NOT_FOUND', 'allocation not found')

    _apply_payload(rec, payload, auth.user_id)
    rec.version += 1
    db.commit()
    db.refresh(rec)
    return PurchaseResultResponse(id=rec.id, allocation_id=rec.allocation_id, result_status=rec.result_status, version=rec.version)


@router.post('/bulk-upsert')
def bulk_upsert_purchase_results(
    payload: PurchaseResultBulkUpsertRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'buyer')),
):
    upserted = 0
    for item in payload.items:
        existing = db.query(PurchaseResult).filter(PurchaseResult.allocation_id == item.allocation_id).one_or_none()
        if existing is None:
            alloc = db.query(SupplierAllocation).filter(SupplierAllocation.id == item.allocation_id).one_or_none()
            if alloc is None:
                api_error(404, 'ALLOCATION_NOT_FOUND', f'allocation not found: {item.allocation_id}')
            rec = PurchaseResult()
            _apply_payload(rec, item, auth.user_id)
            rec.version = 1
            db.add(rec)
        else:
            if existing.version != item.version:
                api_error(409, 'VERSION_CONFLICT', f'version conflict: allocation_id={item.allocation_id}')
            _apply_payload(existing, item, auth.user_id)
            existing.version += 1
        upserted += 1

    db.commit()
    return {'upserted_count': upserted}
