from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.models.entities import InvoiceStatus


class InvoiceCreateRequest(BaseModel):
    order_id: int
    invoice_no: str
    invoice_date: date
    due_date: date | None = None
    created_by: str | None = None


class InvoiceCreateResponse(BaseModel):
    invoice_id: int
    invoice_no: str
    subtotal: Decimal
    tax_total: Decimal
    grand_total: Decimal
    status: InvoiceStatus


class InvoiceFinalizeResponse(BaseModel):
    invoice_id: int
    status: InvoiceStatus
