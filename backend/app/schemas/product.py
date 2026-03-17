from pydantic import BaseModel


class ProductCreate(BaseModel):
    sku: str
    name: str
    order_uom: str
    purchase_uom: str
    invoice_uom: str
    is_catch_weight: bool = False
    weight_capture_required: bool = False
    pricing_basis_default: str = 'uom_count'


class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
