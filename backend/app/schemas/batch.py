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
    error_message: str | None = None


class JobHistoryItem(BaseModel):
    task_id: str
    job_type: str
    order_id: int | None = None
    status: str
    requested_by: str
    requested_at: str
    started_at: str | None = None
    finished_at: str | None = None


class JobHistoryListResponse(BaseModel):
    items: list[JobHistoryItem]
    count: int
