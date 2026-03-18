from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    sku: str
    name: str
    order_uom: str
    purchase_uom: str
    invoice_uom: str
    is_catch_weight: bool = False
    weight_capture_required: bool = False
    pricing_basis_default: str = 'uom_count'


class ProductUpdate(BaseModel):
    name: str | None = None
    order_uom: str | None = None
    purchase_uom: str | None = None
    invoice_uom: str | None = None
    is_catch_weight: bool | None = None
    weight_capture_required: bool | None = None
    active: bool | None = None
    version: int = Field(ge=1)


class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    active: bool
    version: int
