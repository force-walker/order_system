from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


class AllocationRunResponse(BaseModel):
    processed: int


class AllocationOverrideRequest(BaseModel):
    final_supplier_id: int
    final_qty: Decimal = Field(gt=0)
    final_uom: str
    override_reason_code: str
    override_note: str | None = None
    overridden_by: str


class SplitLinePart(BaseModel):
    final_supplier_id: int
    final_qty: Decimal = Field(gt=0)
    final_uom: str


class AllocationSplitLineRequest(BaseModel):
    parts: list[SplitLinePart] = Field(min_length=2)
    override_reason_code: str
    override_note: str | None = None
    overridden_by: str


class AllocationSplitLineResponse(BaseModel):
    split_group_id: str
    allocation_ids: list[int]


class AllocationConfirmRequest(BaseModel):
    allocation_ids: list[int] | None = None


class AllocationConfirmResponse(BaseModel):
    confirmed_count: int
