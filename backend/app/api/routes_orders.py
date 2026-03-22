from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, require_roles
from app.core.errors import api_error
from app.db.session import get_db
from app.models.entities import LineStatus, Order, OrderItem, OrderStatus, PricingBasis
from app.schemas.order import OrderCreate, OrderCreateResponse
from app.schemas.transition import OrderBulkTransitionRequest, OrderBulkTransitionResponse
from app.services.invoice_calc import calc_line

router = APIRouter(prefix='/orders', tags=['orders'])


@router.post('', response_model=OrderCreateResponse)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'order_entry')),
) -> OrderCreateResponse:
    order = Order(
        order_no=payload.order_no,
        customer_id=payload.customer_id,
        order_datetime=payload.order_datetime,
        delivery_date=payload.order_datetime.date(),
        delivery_type=payload.delivery_type,
        delivery_address_snapshot=payload.delivery_address_snapshot,
        payment_method=payload.payment_method,
        payment_status=payload.payment_status,
        note=payload.note,
        created_by=payload.created_by,
        status=OrderStatus.confirmed,
    )
    db.add(order)
    db.flush()

    for item in payload.items:
        if item.pricing_basis == PricingBasis.uom_count:
            subtotal_base = Decimal(item.ordered_qty) * Decimal(item.unit_price_order_uom or 0)
        else:
            weight = item.actual_weight_kg or item.estimated_weight_kg
            if weight is None:
                api_error(400, 'ORDER_WEIGHT_REQUIRED', 'per_kg item requires estimated_weight_kg or actual_weight_kg')
            subtotal_base = Decimal(weight) * Decimal(item.unit_price_per_kg or 0)

        line_subtotal, line_tax, line_total = calc_line(
            subtotal=subtotal_base,
            discount=Decimal(item.discount_amount),
            tax_code=item.tax_code,
        )

        db.add(
            OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                ordered_qty=item.ordered_qty,
                order_uom_type=PricingBasis.uom_count,
                estimated_weight_kg=item.estimated_weight_kg,
                actual_weight_kg=item.actual_weight_kg,
                pricing_basis=item.pricing_basis,
                unit_price_uom_count=item.unit_price_order_uom,
                unit_price_uom_kg=item.unit_price_per_kg,
                discount_amount=item.discount_amount,
                tax_code=item.tax_code,
                line_subtotal=line_subtotal,
                line_tax=line_tax,
                line_total=line_total,
            )
        )

    db.commit()
    return OrderCreateResponse(order_id=order.id, order_no=order.order_no, item_count=len(payload.items))


_TRANSITION_RULES: dict[tuple[OrderStatus, OrderStatus], tuple[LineStatus, LineStatus]] = {
    (OrderStatus.confirmed, OrderStatus.allocated): (LineStatus.open, LineStatus.allocated),
    (OrderStatus.allocated, OrderStatus.purchased): (LineStatus.allocated, LineStatus.purchased),
    (OrderStatus.purchased, OrderStatus.shipped): (LineStatus.purchased, LineStatus.shipped),
    (OrderStatus.shipped, OrderStatus.invoiced): (LineStatus.shipped, LineStatus.invoiced),
}


@router.post('/{order_id}/bulk-transition', response_model=OrderBulkTransitionResponse)
def bulk_transition_order(
    order_id: int,
    payload: OrderBulkTransitionRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'buyer', 'order_entry')),
) -> OrderBulkTransitionResponse:
    order = db.query(Order).filter(Order.id == order_id).one_or_none()
    if order is None:
        api_error(404, 'ORDER_NOT_FOUND', 'order not found')

    key = (payload.from_status, payload.to_status)
    if key not in _TRANSITION_RULES:
        api_error(422, 'INVALID_TRANSITION_PAIR', 'invalid transition pair')

    if order.version != payload.version:
        api_error(409, 'VERSION_CONFLICT', 'record has been updated by another user')

    if order.status != payload.from_status:
        api_error(409, 'ORDER_STATUS_MISMATCH', 'order status mismatch')

    from_line, to_line = _TRANSITION_RULES[key]
    target_lines = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order_id, OrderItem.line_status == from_line)
        .all()
    )

    if not target_lines:
        api_error(409, 'STATUS_NO_TARGET_LINES', 'no eligible lines')

    for line in target_lines:
        line.line_status = to_line
        line.version += 1

    order.status = payload.to_status
    order.version += 1
    db.commit()

    return OrderBulkTransitionResponse(
        order_id=order.id,
        updated_lines=len(target_lines),
        updated_order_status=order.status,
    )
