from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, require_roles
from app.db.session import get_db
from app.models.entities import Invoice, InvoiceItem, InvoiceStatus, Order, OrderItem, PricingBasis
from app.schemas.invoice import InvoiceCreateRequest, InvoiceCreateResponse, InvoiceFinalizeResponse
from app.services.invoice_calc import calc_line, quantize_jpy

router = APIRouter(prefix='/invoices', tags=['invoices'])


@router.post('', response_model=InvoiceCreateResponse)
def create_invoice(
    payload: InvoiceCreateRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'order_entry')),
) -> InvoiceCreateResponse:
    order = db.query(Order).filter(Order.id == payload.order_id).one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail='order not found')

    items = db.query(OrderItem).filter(OrderItem.order_id == order.id, OrderItem.line_status != 'cancelled').all()
    if not items:
        raise HTTPException(status_code=400, detail='no invoiceable items')

    invoice = Invoice(
        invoice_no=payload.invoice_no,
        customer_id=order.customer_id,
        invoice_date=payload.invoice_date,
        delivery_date=order.delivery_date,
        due_date=payload.due_date,
        subtotal=Decimal('0'),
        tax_total=Decimal('0'),
        grand_total=Decimal('0'),
        status=InvoiceStatus.draft,
        created_by=payload.created_by,
    )
    db.add(invoice)
    db.flush()

    subtotal_sum = Decimal('0')
    tax_sum = Decimal('0')
    total_sum = Decimal('0')

    for item in items:
        if item.pricing_basis == PricingBasis.uom_kg:
            if item.actual_weight_kg is None:
                raise HTTPException(status_code=400, detail=f'catch-weight line missing actual_weight_kg: order_item={item.id}')
            if item.unit_price_uom_kg is None:
                raise HTTPException(status_code=400, detail=f'missing unit_price_uom_kg: order_item={item.id}')
            base = Decimal(item.actual_weight_kg) * Decimal(item.unit_price_uom_kg)
            unit_price = Decimal(item.unit_price_uom_kg)
            qty_display = Decimal(item.actual_weight_kg)
            uom_display = 'kg'
            description = f'CatchWeight Item #{item.product_id}'
        else:
            if item.unit_price_uom_count is None:
                raise HTTPException(status_code=400, detail=f'missing unit_price_uom_count: order_item={item.id}')
            base = Decimal(item.ordered_qty) * Decimal(item.unit_price_uom_count)
            unit_price = Decimal(item.unit_price_uom_count)
            qty_display = Decimal(item.ordered_qty)
            uom_display = item.order_uom_type.value
            description = f'Item #{item.product_id}'

        line_subtotal, line_tax, line_total = calc_line(base, Decimal(item.discount_amount or 0), item.tax_code)

        db.add(
            InvoiceItem(
                invoice_id=invoice.id,
                order_item_id=item.id,
                description=description,
                qty_display=qty_display,
                uom_display=uom_display,
                weight_kg=item.actual_weight_kg,
                sales_unit_price=unit_price,
                line_amount=line_subtotal,
                tax_code=item.tax_code,
                tax_amount=line_tax,
            )
        )

        subtotal_sum += line_subtotal
        tax_sum += line_tax
        total_sum += line_total

    invoice.subtotal = quantize_jpy(subtotal_sum)
    invoice.tax_total = quantize_jpy(tax_sum)
    invoice.grand_total = quantize_jpy(total_sum)

    db.commit()

    return InvoiceCreateResponse(
        invoice_id=invoice.id,
        invoice_no=invoice.invoice_no,
        subtotal=invoice.subtotal,
        tax_total=invoice.tax_total,
        grand_total=invoice.grand_total,
        status=invoice.status,
    )


@router.post('/{invoice_id}/finalize', response_model=InvoiceFinalizeResponse)
def finalize_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'order_entry')),
) -> InvoiceFinalizeResponse:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).one_or_none()
    if invoice is None:
        raise HTTPException(status_code=404, detail='invoice not found')

    if invoice.grand_total < 0:
        raise HTTPException(status_code=400, detail='negative invoice total')

    invoice.status = InvoiceStatus.finalized
    db.commit()
    return InvoiceFinalizeResponse(invoice_id=invoice.id, status=invoice.status)
