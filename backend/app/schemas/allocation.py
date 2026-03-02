from decimal import Decimal

from pydantic import BaseModel, Field


class AllocationRunResponse(BaseModel):
    processed: int


class AllocationOverrideRequest(BaseModel):
    final_supplier_id: int
    final_qty: Decimal = Field(gt=0)
    final_uom: str
    override_reason_code: str
    override_note: str | None = None
    overridden_by: str


class AllocationConfirmRequest(BaseModel):
    allocation_ids: list[int] | None = None


class AllocationConfirmResponse(BaseModel):
    confirmed_count: int
