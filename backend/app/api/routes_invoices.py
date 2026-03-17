from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, require_roles
from app.core.errors import api_error
from app.db.session import get_db
from app.models.entities import AuditAction, AuditLog, Invoice, InvoiceItem, InvoiceLineStatus, InvoiceStatus, Order, OrderItem, PricingBasis
from app.schemas.invoice import (
    InvoiceCreateRequest,
    InvoiceCreateResponse,
    InvoiceFinalizeResponse,
    InvoiceResetRequest,
    InvoiceResetResponse,
    InvoiceUnlockRequest,
    InvoiceUnlockResponse,
)
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
        api_error(404, 'ORDER_NOT_FOUND', 'order not found')

    items = db.query(OrderItem).filter(OrderItem.order_id == order.id, OrderItem.line_status != 'cancelled').all()
    if not items:
        api_error(400, 'NO_INVOICEABLE_ITEMS', 'no invoiceable items')

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
                api_error(400, 'CATCH_WEIGHT_REQUIRED', f'catch-weight line missing actual_weight_kg: order_item={item.id}')
            if item.unit_price_uom_kg is None:
                api_error(400, 'UNIT_PRICE_UOM_KG_REQUIRED', f'missing unit_price_uom_kg: order_item={item.id}')
            base = Decimal(item.actual_weight_kg) * Decimal(item.unit_price_uom_kg)
            unit_price = Decimal(item.unit_price_uom_kg)
            qty_display = Decimal(item.actual_weight_kg)
            uom_display = 'kg'
            description = f'CatchWeight Item #{item.product_id}'
        else:
            if item.unit_price_uom_count is None:
                api_error(400, 'UNIT_PRICE_UOM_COUNT_REQUIRED', f'missing unit_price_uom_count: order_item={item.id}')
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
        api_error(404, 'INVOICE_NOT_FOUND', 'invoice not found')

    if invoice.grand_total < 0:
        api_error(400, 'NEGATIVE_INVOICE_TOTAL', 'negative invoice total')

    if invoice.status != InvoiceStatus.draft:
        api_error(409, 'INVOICE_NOT_DRAFT', 'invoice is not draft')

    invoice.status = InvoiceStatus.finalized
    invoice.is_locked = True
    invoice.locked_at = datetime.utcnow()
    invoice.version += 1
    db.commit()
    return InvoiceFinalizeResponse(invoice_id=invoice.id, status=invoice.status, is_locked=invoice.is_locked)


@router.post('/{invoice_id}/reset-to-draft', response_model=InvoiceResetResponse)
def reset_invoice_to_draft(
    invoice_id: int,
    payload: InvoiceResetRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'order_entry')),
) -> InvoiceResetResponse:
    allowed_codes = {'data_error', 'pricing_error', 'tax_error', 'customer_change', 'policy_exception'}
    if payload.reset_reason_code not in allowed_codes:
        api_error(422, 'INVALID_RESET_REASON_CODE', 'invalid reset_reason_code')

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).one_or_none()
    if invoice is None:
        api_error(404, 'INVOICE_NOT_FOUND', 'invoice not found')
    if invoice.version != payload.version:
        api_error(409, 'VERSION_CONFLICT', 'record has been updated by another user')
    if invoice.status != InvoiceStatus.finalized:
        api_error(409, 'INVOICE_NOT_FINALIZED', 'only finalized invoice can reset to draft')

    invoice.status = InvoiceStatus.draft
    invoice.is_locked = False
    invoice.version += 1
    invoice.locked_at = None
    invoice.version += 1

    db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).update(
        {InvoiceItem.invoice_line_status: InvoiceLineStatus.uninvoiced}, synchronize_session=False
    )

    db.add(
        AuditLog(
            entity_type='invoice',
            entity_id=invoice.id,
            action=AuditAction.status_change,
            before_json={'status': 'finalized'},
            after_json={'status': 'draft'},
            reason_code=payload.reset_reason_code,
            changed_by=auth.user_id,
        )
    )

    db.commit()
    return InvoiceResetResponse(invoice_id=invoice.id, status=invoice.status)


@router.post('/{invoice_id}/unlock', response_model=InvoiceUnlockResponse)
def unlock_invoice(
    invoice_id: int,
    payload: InvoiceUnlockRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin')),
) -> InvoiceUnlockResponse:
    allowed_codes = {
        'pricing_correction',
        'quantity_correction',
        'tax_correction',
        'customer_request',
        'data_fix',
        'other',
    }
    if payload.unlock_reason_code not in allowed_codes:
        api_error(422, 'INVALID_UNLOCK_REASON_CODE', 'invalid unlock_reason_code')

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).one_or_none()
    if invoice is None:
        api_error(404, 'INVOICE_NOT_FOUND', 'invoice not found')
    if invoice.version != payload.version:
        api_error(409, 'VERSION_CONFLICT', 'record has been updated by another user')
    if invoice.status != InvoiceStatus.finalized or not invoice.is_locked:
        api_error(409, 'INVOICE_NOT_LOCKED_FINALIZED', 'target must be finalized and locked')

    invoice.is_locked = False
    invoice.version += 1

    db.add(
        AuditLog(
            entity_type='invoice',
            entity_id=invoice.id,
            action=AuditAction.override,
            before_json={'is_locked': True, 'status': 'finalized'},
            after_json={'is_locked': False, 'status': 'finalized', 'reason_note': payload.reason_note},
            reason_code=payload.unlock_reason_code,
            changed_by=auth.user_id,
        )
    )

    db.commit()
    return InvoiceUnlockResponse(invoice_id=invoice.id, status=invoice.status, is_locked=invoice.is_locked)
