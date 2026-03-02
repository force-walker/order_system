from pydantic import BaseModel


class ProductCreate(BaseModel):
    sku: str
    name: str
    order_uom: str
    purchase_uom: str
    invoice_uom: str
    is_catch_weight: bool = False
    weight_capture_required: bool = False
    pricing_basis_default: str = 'per_order_uom'


class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
