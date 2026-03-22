import enum
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


JSON_COMPAT = JSON().with_variant(JSONB, 'postgresql')


class PricingBasis(str, enum.Enum):
    uom_count = 'uom_count'
    uom_kg = 'uom_kg'


class StockoutPolicy(str, enum.Enum):
    backorder = 'backorder'
    substitute = 'substitute'
    cancel = 'cancel'
    split = 'split'


class OrderStatus(str, enum.Enum):
    new = 'new'
    confirmed = 'confirmed'
    allocated = 'allocated'
    purchased = 'purchased'
    shipped = 'shipped'
    invoiced = 'invoiced'
    cancelled = 'cancelled'


class LineStatus(str, enum.Enum):
    open = 'open'
    allocated = 'allocated'
    purchased = 'purchased'
    shipped = 'shipped'
    invoiced = 'invoiced'
    cancelled = 'cancelled'


class InvoiceStatus(str, enum.Enum):
    draft = 'draft'
    finalized = 'finalized'
    sent = 'sent'
    cancelled = 'cancelled'


class InvoiceLineStatus(str, enum.Enum):
    uninvoiced = 'uninvoiced'
    partially_invoiced = 'partially_invoiced'
    invoiced = 'invoiced'
    cancelled = 'cancelled'


class AuditAction(str, enum.Enum):
    create = 'create'
    update = 'update'
    status_change = 'status_change'
    override = 'override'


class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[int] = mapped_column(default=1)


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
    pricing_basis_default: Mapped[PricingBasis] = mapped_column(Enum(PricingBasis), default=PricingBasis.uom_count)
    rounding_weight_scale: Mapped[int] = mapped_column(default=3)
    rounding_amount_scale: Mapped[int] = mapped_column(default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[int] = mapped_column(default=1)


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_no: Mapped[str] = mapped_column(String(64), unique=True)
    customer_id: Mapped[int] = mapped_column(index=True)
    order_datetime: Mapped[datetime] = mapped_column(DateTime, index=True)
    delivery_date: Mapped[date] = mapped_column(Date, index=True)
    delivery_type: Mapped[str] = mapped_column(String(32))
    delivery_address_snapshot: Mapped[str | None] = mapped_column(Text)
    payment_method: Mapped[str | None] = mapped_column(String(64))
    payment_status: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.new, index=True)
    note: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[int] = mapped_column(default=1)


class OrderItem(Base):
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), index=True)
    ordered_qty: Mapped[float] = mapped_column(Numeric(12, 3))
    order_uom_type: Mapped[PricingBasis] = mapped_column(Enum(PricingBasis), default=PricingBasis.uom_count)
    estimated_weight_kg: Mapped[float | None] = mapped_column(Numeric(12, 3))
    actual_weight_kg: Mapped[float | None] = mapped_column(Numeric(12, 3))
    pricing_basis: Mapped[PricingBasis] = mapped_column(Enum(PricingBasis), default=PricingBasis.uom_count)
    unit_price_uom_count: Mapped[float | None] = mapped_column(Numeric(12, 2))
    unit_price_uom_kg: Mapped[float | None] = mapped_column(Numeric(12, 2))
    discount_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    tax_code: Mapped[str] = mapped_column(String(32))
    line_subtotal: Mapped[float | None] = mapped_column(Numeric(12, 2))
    line_tax: Mapped[float | None] = mapped_column(Numeric(12, 2))
    line_total: Mapped[float | None] = mapped_column(Numeric(12, 2))
    line_status: Mapped[LineStatus] = mapped_column(Enum(LineStatus), default=LineStatus.open, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[int] = mapped_column(default=1)


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
    target_price: Mapped[float | None] = mapped_column(Numeric(12, 2))
    stockout_policy: Mapped[StockoutPolicy | None] = mapped_column(Enum(StockoutPolicy))
    is_manual_override: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    override_reason_code: Mapped[str | None] = mapped_column(String(64))
    override_note: Mapped[str | None] = mapped_column(Text)
    overridden_by: Mapped[str | None] = mapped_column(String(64))
    overridden_at: Mapped[datetime | None] = mapped_column(DateTime)
    split_group_id: Mapped[str | None] = mapped_column(String(64), index=True)
    parent_allocation_id: Mapped[int | None] = mapped_column(ForeignKey('supplier_allocations.id'), index=True)
    is_split_child: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[int] = mapped_column(default=1)


class PurchaseResult(Base):
    __tablename__ = 'purchase_results'

    id: Mapped[int] = mapped_column(primary_key=True)
    allocation_id: Mapped[int] = mapped_column(ForeignKey('supplier_allocations.id'), index=True)
    supplier_id: Mapped[int | None] = mapped_column(index=True)
    purchased_qty: Mapped[float] = mapped_column(Numeric(12, 3))
    purchased_uom: Mapped[str] = mapped_column(String(32))
    actual_weight_kg: Mapped[float | None] = mapped_column(Numeric(12, 3))
    unit_cost: Mapped[float | None] = mapped_column(Numeric(12, 2))
    final_unit_cost: Mapped[float | None] = mapped_column(Numeric(12, 2))
    result_status: Mapped[str] = mapped_column(String(32), index=True)
    shortage_qty: Mapped[float | None] = mapped_column(Numeric(12, 3))
    shortage_policy: Mapped[StockoutPolicy | None] = mapped_column(Enum(StockoutPolicy))
    invoiceable_flag: Mapped[bool] = mapped_column(Boolean, default=True)
    recorded_by: Mapped[str] = mapped_column(String(64))
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[int] = mapped_column(default=1)
    note: Mapped[str | None] = mapped_column(Text)


class Invoice(Base):
    __tablename__ = 'invoices'

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_no: Mapped[str] = mapped_column(String(64), unique=True)
    customer_id: Mapped[int] = mapped_column(index=True)
    invoice_date: Mapped[date] = mapped_column(Date)
    delivery_date: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date | None] = mapped_column(Date)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2))
    tax_total: Mapped[float] = mapped_column(Numeric(12, 2))
    grand_total: Mapped[float] = mapped_column(Numeric(12, 2))
    status: Mapped[InvoiceStatus] = mapped_column(Enum(InvoiceStatus), default=InvoiceStatus.draft, index=True)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_by: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[int] = mapped_column(default=1)


class InvoiceItem(Base):
    __tablename__ = 'invoice_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey('invoices.id'))
    order_item_id: Mapped[int] = mapped_column(ForeignKey('order_items.id'), index=True)
    description: Mapped[str] = mapped_column(String(255))
    qty_display: Mapped[float] = mapped_column(Numeric(12, 3))
    uom_display: Mapped[str] = mapped_column(String(32))
    weight_kg: Mapped[float | None] = mapped_column(Numeric(12, 3))
    billable_qty: Mapped[float | None] = mapped_column(Numeric(12, 3))
    billable_uom: Mapped[str | None] = mapped_column(String(32))
    sales_unit_price: Mapped[float] = mapped_column(Numeric(12, 2))
    line_amount: Mapped[float] = mapped_column(Numeric(12, 2))
    tax_code: Mapped[str] = mapped_column(String(32))
    tax_amount: Mapped[float] = mapped_column(Numeric(12, 2))
    unit_cost_basis: Mapped[float | None] = mapped_column(Numeric(12, 2))
    invoice_line_status: Mapped[InvoiceLineStatus] = mapped_column(
        Enum(InvoiceLineStatus, name='invoice_line_status'), default=InvoiceLineStatus.uninvoiced
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[int] = mapped_column(default=1)


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[int] = mapped_column(index=True)
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction))
    before_json: Mapped[dict | None] = mapped_column(JSON_COMPAT)
    after_json: Mapped[dict | None] = mapped_column(JSON_COMPAT)
    reason_code: Mapped[str | None] = mapped_column(String(64))
    changed_by: Mapped[str] = mapped_column(String(64))
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (UniqueConstraint('id', 'entity_type', name='uq_audit_id_entity'),)


class BatchJobHistory(Base):
    __tablename__ = 'batch_job_histories'

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    parent_task_id: Mapped[str | None] = mapped_column(String(64), index=True)
    job_type: Mapped[str] = mapped_column(String(64), index=True)
    order_id: Mapped[int | None] = mapped_column(index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    requested_by: Mapped[str] = mapped_column(String(64))
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    retry_count: Mapped[int] = mapped_column(default=0)
    max_retries: Mapped[int] = mapped_column(default=3)
    result_json: Mapped[dict | None] = mapped_column(JSON_COMPAT)
    error_message: Mapped[str | None] = mapped_column(Text)
