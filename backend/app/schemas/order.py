from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.models.entities import PricingBasis


class OrderItemCreate(BaseModel):
    product_id: int
    ordered_qty: Decimal = Field(gt=0)
    ordered_uom: str
    estimated_weight_kg: Decimal | None = None
    actual_weight_kg: Decimal | None = None
    pricing_basis: PricingBasis
    unit_price_order_uom: Decimal | None = None
    unit_price_per_kg: Decimal | None = None
    discount_amount: Decimal = Decimal('0')
    tax_code: str = 'standard'

    @model_validator(mode='after')
    def validate_price_basis(self):
        if self.pricing_basis == PricingBasis.per_order_uom and self.unit_price_order_uom is None:
            raise ValueError('unit_price_order_uom is required when pricing_basis=per_order_uom')
        if self.pricing_basis == PricingBasis.per_kg and self.unit_price_per_kg is None:
            raise ValueError('unit_price_per_kg is required when pricing_basis=per_kg')
        return self


class OrderCreate(BaseModel):
    order_no: str
    customer_id: int
    order_datetime: datetime
    delivery_type: str
    delivery_address_snapshot: str | None = None
    payment_method: str | None = None
    payment_status: str | None = None
    note: str | None = None
    created_by: str | None = None
    items: list[OrderItemCreate]


class OrderCreateResponse(BaseModel):
    order_id: int
    order_no: str
    item_count: int
