from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

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
    is_locked: bool


class InvoiceResetRequest(BaseModel):
    version: int = Field(ge=1)
    reset_reason_code: str
    reason_note: str | None = Field(default=None, max_length=500)


class InvoiceResetResponse(BaseModel):
    invoice_id: int
    status: InvoiceStatus


class InvoiceUnlockRequest(BaseModel):
    version: int = Field(ge=1)
    unlock_reason_code: str
    reason_note: str | None = Field(default=None, max_length=500)


class InvoiceUnlockResponse(BaseModel):
    invoice_id: int
    status: InvoiceStatus
    is_locked: bool
