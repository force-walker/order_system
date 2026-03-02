import enum
from datetime import datetime, date

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PricingBasis(str, enum.Enum):
    per_order_uom = 'per_order_uom'
    per_kg = 'per_kg'


class OrderStatus(str, enum.Enum):
    new = 'new'
    confirmed = 'confirmed'
    purchasing = 'purchasing'
    shipped = 'shipped'
    delivered = 'delivered'
    completed = 'completed'
    cancelled = 'cancelled'


class LineStatus(str, enum.Enum):
    open = 'open'
    allocated = 'allocated'
    purchased = 'purchased'
    invoiced = 'invoiced'
    cancelled = 'cancelled'


class ResultStatus(str, enum.Enum):
    full = 'full'
    partial = 'partial'
    failed = 'failed'
    substitute = 'substitute'


class InvoiceStatus(str, enum.Enum):
    draft = 'draft'
    finalized = 'finalized'
    sent = 'sent'
    paid = 'paid'
    cancelled = 'cancelled'


class AuditAction(str, enum.Enum):
    create = 'create'
    update = 'update'
    status_change = 'status_change'
    override = 'override'


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    order_uom: Mapped[str] = mapped_column(String(32))
    purchase_uom: Mapped[str] = mapped_column(String(32))
    invoice_uom: Mapped[str] = mapped_column(String(32))
    is_catch_weight: Mapped[bool] = mapped_column(Boolean, default=False)
    weight_capture_required: Mapped[bool] = mapped_column(Boolean, default=False)
    pricing_basis_default: Mapped[PricingBasis] = mapped_column(Enum(PricingBasis), default=PricingBasis.per_order_uom)
    rounding_weight_scale: Mapped[int] = mapped_column(default=3)
    rounding_amount_scale: Mapped[int] = mapped_column(default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_no: Mapped[str] = mapped_column(String(64), unique=True)
    customer_id: Mapped[int] = mapped_column(index=True)
    order_datetime: Mapped[datetime] = mapped_column(DateTime, index=True)
    delivery_type: Mapped[str] = mapped_column(String(32))
    delivery_address_snapshot: Mapped[str | None] = mapped_column(Text)
    payment_method: Mapped[str | None] = mapped_column(String(64))
    payment_status: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.new, index=True)
    note: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OrderItem(Base):
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), index=True)
    ordered_qty: Mapped[float] = mapped_column(Numeric(12, 3))
    ordered_uom: Mapped[str] = mapped_column(String(32))
    estimated_weight_kg: Mapped[float | None] = mapped_column(Numeric(12, 3))
    actual_weight_kg: Mapped[float | None] = mapped_column(Numeric(12, 3))
    pricing_basis: Mapped[PricingBasis] = mapped_column(Enum(PricingBasis), default=PricingBasis.per_order_uom)
    unit_price_order_uom: Mapped[float | None] = mapped_column(Numeric(12, 2))
    unit_price_per_kg: Mapped[float | None] = mapped_column(Numeric(12, 2))
    discount_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    tax_code: Mapped[str] = mapped_column(String(32))
    line_subtotal: Mapped[float | None] = mapped_column(Numeric(12, 2))
    line_tax: Mapped[float | None] = mapped_column(Numeric(12, 2))
    line_total: Mapped[float | None] = mapped_column(Numeric(12, 2))
    line_status: Mapped[LineStatus] = mapped_column(Enum(LineStatus), default=LineStatus.open, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SupplierAllocation(Base):
    __tablename__ = 'supplier_allocations'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_item_id: Mapped[int] = mapped_column(ForeignKey('order_items.id'), index=True)
    suggested_supplier_id: Mapped[int | None] = mapped_column(index=True)
    final_supplier_id: Mapped[int | None] = mapped_column(index=True)
    suggested_qty: Mapped[float | None] = mapped_column(Numeric(12, 3))
    suggested_uom: Mapped[str | None] = mapped_column(String(32))
    final_qty: Mapped[float | None] = mapped_column(Numeric(12, 3))
    final_uom: Mapped[str | None] = mapped_column(String(32))
    is_manual_override: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    override_reason_code: Mapped[str | None] = mapped_column(String(64))
    override_note: Mapped[str | None] = mapped_column(Text)
    overridden_by: Mapped[str | None] = mapped_column(String(64))
    overridden_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PurchaseResult(Base):
    __tablename__ = 'purchase_results'

    id: Mapped[int] = mapped_column(primary_key=True)
    allocation_id: Mapped[int] = mapped_column(ForeignKey('supplier_allocations.id'), index=True)
    purchased_qty: Mapped[float] = mapped_column(Numeric(12, 3))
    purchased_uom: Mapped[str] = mapped_column(String(32))
    actual_weight_kg: Mapped[float | None] = mapped_column(Numeric(12, 3))
    unit_cost: Mapped[float | None] = mapped_column(Numeric(12, 2))
    result_status: Mapped[ResultStatus] = mapped_column(Enum(ResultStatus), index=True)
    recorded_by: Mapped[str] = mapped_column(String(64))
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    note: Mapped[str | None] = mapped_column(Text)


class Invoice(Base):
    __tablename__ = 'invoices'

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_no: Mapped[str] = mapped_column(String(64), unique=True)
    customer_id: Mapped[int] = mapped_column(index=True)
    invoice_date: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date | None] = mapped_column(Date)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2))
    tax_total: Mapped[float] = mapped_column(Numeric(12, 2))
    grand_total: Mapped[float] = mapped_column(Numeric(12, 2))
    status: Mapped[InvoiceStatus] = mapped_column(Enum(InvoiceStatus), default=InvoiceStatus.draft)
    created_by: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InvoiceItem(Base):
    __tablename__ = 'invoice_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey('invoices.id'))
    order_item_id: Mapped[int] = mapped_column(ForeignKey('order_items.id'))
    description: Mapped[str] = mapped_column(String(255))
    qty_display: Mapped[float] = mapped_column(Numeric(12, 3))
    uom_display: Mapped[str] = mapped_column(String(32))
    weight_kg: Mapped[float | None] = mapped_column(Numeric(12, 3))
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2))
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    tax_code: Mapped[str] = mapped_column(String(32))
    tax_amount: Mapped[float] = mapped_column(Numeric(12, 2))


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[int] = mapped_column(index=True)
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction))
    before_json: Mapped[dict | None] = mapped_column(JSONB)
    after_json: Mapped[dict | None] = mapped_column(JSONB)
    reason_code: Mapped[str | None] = mapped_column(String(64))
    changed_by: Mapped[str] = mapped_column(String(64))
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (UniqueConstraint('id', 'entity_type', name='uq_audit_id_entity'),)
