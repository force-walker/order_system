from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import AuthContext, require_roles
from app.db.session import get_db
from app.models.entities import LineStatus, Order, OrderItem, OrderStatus

router = APIRouter(prefix='/transitions/orders', tags=['transitions'])


@router.post('/confirmed-to-allocated')
def transition_confirmed_to_allocated(
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_roles('admin', 'buyer')),
):
    target_items = (
        db.query(OrderItem)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status == OrderStatus.confirmed, OrderItem.line_status == LineStatus.open)
        .all()
    )

    if not target_items:
        raise HTTPException(status_code=409, detail={'code': 'STATUS_NO_TARGET_LINES', 'message': 'no eligible lines'})

    touched_order_ids: set[int] = set()
    for item in target_items:
        item.line_status = LineStatus.allocated
        touched_order_ids.add(item.order_id)

    for order_id in touched_order_ids:
        order = db.query(Order).filter(Order.id == order_id).one()
        order.status = OrderStatus.allocated

    db.commit()
    return {'updated_lines': len(target_items), 'updated_orders': len(touched_order_ids)}
