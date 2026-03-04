from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Order, OrderItem, OrderStatus, PricingBasis
from app.schemas.order import OrderCreate, OrderCreateResponse
from app.services.invoice_calc import calc_line

router = APIRouter(prefix='/orders', tags=['orders'])


@router.post('', response_model=OrderCreateResponse)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)) -> OrderCreateResponse:
    order = Order(
        order_no=payload.order_no,
        customer_id=payload.customer_id,
        order_datetime=payload.order_datetime,
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
        if item.pricing_basis == PricingBasis.per_order_uom:
            subtotal_base = Decimal(item.ordered_qty) * Decimal(item.unit_price_order_uom or 0)
        else:
            weight = item.actual_weight_kg or item.estimated_weight_kg
            if weight is None:
                raise HTTPException(status_code=400, detail='per_kg item requires estimated_weight_kg or actual_weight_kg')
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
                ordered_uom=item.ordered_uom,
                estimated_weight_kg=item.estimated_weight_kg,
                actual_weight_kg=item.actual_weight_kg,
                pricing_basis=item.pricing_basis,
                unit_price_order_uom=item.unit_price_order_uom,
                unit_price_per_kg=item.unit_price_per_kg,
                discount_amount=item.discount_amount,
                tax_code=item.tax_code,
                line_subtotal=line_subtotal,
                line_tax=line_tax,
                line_total=line_total,
            )
        )

    db.commit()
    return OrderCreateResponse(order_id=order.id, order_no=order.order_no, item_count=len(payload.items))
