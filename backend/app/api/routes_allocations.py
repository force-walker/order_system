from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, require_roles
from app.core.errors import api_error
from app.db.session import get_db
from app.models.entities import AuditAction, AuditLog, LineStatus, Order, OrderItem, SupplierAllocation
from app.schemas.allocation import (
    AllocationConfirmRequest,
    AllocationConfirmResponse,
    AllocationOverrideRequest,
    AllocationRunResponse,
    AllocationSplitLineRequest,
    AllocationSplitLineResponse,
)

router = APIRouter(prefix='/allocations', tags=['allocations'])


@router.post('/run-auto', response_model=AllocationRunResponse)
def run_auto_allocation(
    default_supplier_id: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'buyer')),
) -> AllocationRunResponse:
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
        alloc.suggested_uom = item.order_uom_type.value
        alloc.final_qty = alloc.final_qty or item.ordered_qty
        alloc.final_uom = alloc.final_uom or item.order_uom_type.value
        item.line_status = LineStatus.allocated
        processed += 1

    db.commit()
    return AllocationRunResponse(processed=processed)


@router.patch('/{allocation_id}/override')
def override_allocation(
    allocation_id: int,
    payload: AllocationOverrideRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'buyer')),
):
    alloc = db.query(SupplierAllocation).filter(SupplierAllocation.id == allocation_id).one_or_none()
    if alloc is None:
        api_error(404, 'ALLOCATION_NOT_FOUND', 'allocation not found')

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


@router.post('/{allocation_id}/split-line', response_model=AllocationSplitLineResponse)
def split_line(
    allocation_id: int,
    payload: AllocationSplitLineRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'buyer')),
) -> AllocationSplitLineResponse:
    alloc = db.query(SupplierAllocation).filter(SupplierAllocation.id == allocation_id).one_or_none()
    if alloc is None:
        api_error(404, 'ALLOCATION_NOT_FOUND', 'allocation not found')

    target_qty = Decimal(alloc.final_qty or alloc.suggested_qty or 0)
    if target_qty <= 0:
        api_error(400, 'ALLOCATION_INVALID_TARGET_QTY', 'allocation has invalid target qty')

    sum_parts = sum((Decimal(p.final_qty) for p in payload.parts), Decimal('0'))
    if sum_parts != target_qty:
        api_error(400, 'SPLIT_QTY_MISMATCH', f'split qty mismatch: expected={target_qty} actual={sum_parts}')

    split_group_id = f"SPLIT-{uuid4().hex[:12]}"
    child_ids: list[int] = []

    for part in payload.parts:
        child = SupplierAllocation(
            order_item_id=alloc.order_item_id,
            suggested_supplier_id=alloc.suggested_supplier_id,
            final_supplier_id=part.final_supplier_id,
            suggested_qty=alloc.suggested_qty,
            suggested_uom=alloc.suggested_uom,
            final_qty=part.final_qty,
            final_uom=part.final_uom,
            is_manual_override=True,
            override_reason_code=payload.override_reason_code,
            override_note=payload.override_note,
            overridden_by=payload.overridden_by,
            overridden_at=datetime.utcnow(),
            split_group_id=split_group_id,
            parent_allocation_id=alloc.id,
            is_split_child=True,
        )
        db.add(child)
        db.flush()
        child_ids.append(child.id)

    alloc.is_manual_override = True
    alloc.override_reason_code = payload.override_reason_code
    alloc.override_note = payload.override_note
    alloc.overridden_by = payload.overridden_by
    alloc.overridden_at = datetime.utcnow()
    alloc.split_group_id = split_group_id

    db.add(
        AuditLog(
            entity_type='allocation',
            entity_id=alloc.id,
            action=AuditAction.override,
            before_json={
                'final_supplier_id': alloc.final_supplier_id,
                'final_qty': str(target_qty),
                'final_uom': alloc.final_uom,
            },
            after_json={
                'split_group_id': split_group_id,
                'child_allocation_ids': child_ids,
            },
            reason_code=payload.override_reason_code,
            changed_by=payload.overridden_by,
        )
    )

    db.commit()
    return AllocationSplitLineResponse(split_group_id=split_group_id, allocation_ids=child_ids)


@router.post('/confirm', response_model=AllocationConfirmResponse)
def confirm_allocations(
    payload: AllocationConfirmRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'buyer')),
) -> AllocationConfirmResponse:
    q = db.query(SupplierAllocation)
    if payload.allocation_ids:
        q = q.filter(SupplierAllocation.id.in_(payload.allocation_ids))

    allocations = q.all()
    for alloc in allocations:
        if not alloc.final_supplier_id or not alloc.final_qty or alloc.final_qty <= 0:
            api_error(400, 'ALLOCATION_INVALID', f'invalid allocation: {alloc.id}')

    split_group_ids = {a.split_group_id for a in allocations if a.split_group_id}
    for group_id in split_group_ids:
        group_allocs = db.query(SupplierAllocation).filter(SupplierAllocation.split_group_id == group_id).all()
        parent = next((a for a in group_allocs if not a.is_split_child), None)
        children = [a for a in group_allocs if a.is_split_child]

        if parent is None:
            api_error(400, 'SPLIT_GROUP_MISSING_PARENT', f'split group missing parent: {group_id}')
        if len(children) < 2:
            api_error(400, 'SPLIT_GROUP_MIN_CHILDREN', f'split group requires >=2 children: {group_id}')

        parent_qty = Decimal(parent.final_qty or parent.suggested_qty or 0)
        sum_children = sum((Decimal(c.final_qty or 0) for c in children), Decimal('0'))
        if sum_children != parent_qty:
            api_error(400, 'SPLIT_GROUP_QTY_MISMATCH', f'split group qty mismatch: group={group_id} parent={parent_qty} children={sum_children}')

        parent_uom = parent.final_uom or parent.suggested_uom
        if parent_uom and any((c.final_uom != parent_uom for c in children)):
            api_error(400, 'SPLIT_GROUP_UOM_MISMATCH', f'split group uom mismatch: {group_id}')

    return AllocationConfirmResponse(confirmed_count=len(allocations))
