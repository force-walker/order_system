from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


_ALLOWED_RESULT_STATUS = {'not_filled', 'filled', 'partially_filled', 'substituted'}


class PurchaseResultUpsertRequest(BaseModel):
    allocation_id: int
    supplier_id: int | None = None
    purchased_qty: Decimal = Field(gt=0)
    purchased_uom: str
    actual_weight_kg: Decimal | None = None
    unit_cost: Decimal | None = None
    final_unit_cost: Decimal | None = None
    result_status: str
    shortage_qty: Decimal | None = None
    shortage_policy: str | None = None
    invoiceable_flag: bool = True
    note: str | None = None
    version: int = Field(default=1, ge=1)

    @model_validator(mode='after')
    def validate_consistency(self):
        if self.result_status not in _ALLOWED_RESULT_STATUS:
            raise ValueError('invalid result_status')
        if self.result_status == 'not_filled' and self.invoiceable_flag:
            raise ValueError('not_filled result cannot be invoiceable')
        return self


class PurchaseResultBulkUpsertRequest(BaseModel):
    items: list[PurchaseResultUpsertRequest] = Field(min_length=1)


class PurchaseResultResponse(BaseModel):
    id: int
    allocation_id: int
    result_status: str
    version: int
