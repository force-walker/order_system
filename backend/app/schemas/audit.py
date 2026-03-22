from datetime import datetime

from pydantic import BaseModel


class AuditLogItem(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    action: str
    reason_code: str | None = None
    changed_by: str
    changed_at: datetime
    before_json: dict | None = None
    after_json: dict | None = None


class AuditLogListResponse(BaseModel):
    items: list[AuditLogItem]
    count: int
