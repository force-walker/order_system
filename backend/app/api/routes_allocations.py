from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import AuditAction, AuditLog, LineStatus, Order, OrderItem, SupplierAllocation
from app.schemas.allocation import (
    AllocationConfirmRequest,
    AllocationConfirmResponse,
    AllocationOverrideRequest,
    AllocationRunResponse,
)

router = APIRouter(prefix='/allocations', tags=['allocations'])


@router.post('/run-auto', response_model=AllocationRunResponse)
def run_auto_allocation(default_supplier_id: int = Query(1, ge=1), db: Session = Depends(get_db)) -> AllocationRunResponse:
    items = (
        db.query(OrderItem)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status == 'confirmed', OrderItem.line_status == LineStatus.open)
        .all()
    )

    processed = 0
    for item in items:
        alloc = db.query(SupplierAllocation).filter(SupplierAllocation.order_item_id == item.id).one_or_none()
        if alloc is None:
            alloc = SupplierAllocation(order_item_id=item.id)
            db.add(alloc)

        alloc.suggested_supplier_id = default_supplier_id
        alloc.final_supplier_id = alloc.final_supplier_id or default_supplier_id
        alloc.suggested_qty = item.ordered_qty
        alloc.suggested_uom = item.ordered_uom
        alloc.final_qty = alloc.final_qty or item.ordered_qty
        alloc.final_uom = alloc.final_uom or item.ordered_uom
        item.line_status = LineStatus.allocated
        processed += 1

    db.commit()
    return AllocationRunResponse(processed=processed)


@router.patch('/{allocation_id}/override')
def override_allocation(allocation_id: int, payload: AllocationOverrideRequest, db: Session = Depends(get_db)):
    alloc = db.query(SupplierAllocation).filter(SupplierAllocation.id == allocation_id).one_or_none()
    if alloc is None:
        raise HTTPException(status_code=404, detail='allocation not found')

    before = {
        'final_supplier_id': alloc.final_supplier_id,
        'final_qty': str(alloc.final_qty) if alloc.final_qty is not None else None,
        'final_uom': alloc.final_uom,
    }

    alloc.final_supplier_id = payload.final_supplier_id
    alloc.final_qty = Decimal(payload.final_qty)
    alloc.final_uom = payload.final_uom
    alloc.is_manual_override = True
    alloc.override_reason_code = payload.override_reason_code
    alloc.override_note = payload.override_note
    alloc.overridden_by = payload.overridden_by
    alloc.overridden_at = datetime.utcnow()

    db.add(
        AuditLog(
            entity_type='allocation',
            entity_id=alloc.id,
            action=AuditAction.override,
            before_json=before,
            after_json={
                'final_supplier_id': payload.final_supplier_id,
                'final_qty': str(payload.final_qty),
                'final_uom': payload.final_uom,
            },
            reason_code=payload.override_reason_code,
            changed_by=payload.overridden_by,
        )
    )
    db.commit()
    return {'ok': True, 'allocation_id': alloc.id}


@router.post('/confirm', response_model=AllocationConfirmResponse)
def confirm_allocations(payload: AllocationConfirmRequest, db: Session = Depends(get_db)) -> AllocationConfirmResponse:
    q = db.query(SupplierAllocation)
    if payload.allocation_ids:
        q = q.filter(SupplierAllocation.id.in_(payload.allocation_ids))

    allocations = q.all()
    for alloc in allocations:
        if not alloc.final_supplier_id or not alloc.final_qty or alloc.final_qty <= 0:
            raise HTTPException(status_code=400, detail=f'invalid allocation: {alloc.id}')

    return AllocationConfirmResponse(confirmed_count=len(allocations))
