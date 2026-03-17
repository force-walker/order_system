from pydantic import BaseModel

from app.models.entities import OrderStatus


class OrderBulkTransitionRequest(BaseModel):
    from_status: OrderStatus
    to_status: OrderStatus


class OrderBulkTransitionResponse(BaseModel):
    order_id: int
    updated_lines: int
    updated_order_status: OrderStatus
