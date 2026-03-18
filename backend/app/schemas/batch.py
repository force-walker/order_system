from pydantic import BaseModel, Field


class ProcurementRegenerationRequest(BaseModel):
    order_id: int = Field(ge=1)


class JobEnqueueResponse(BaseModel):
    task_id: str
    status: str


class JobStatusResponse(BaseModel):
    task_id: str
    status: str
    result: dict | None = None
