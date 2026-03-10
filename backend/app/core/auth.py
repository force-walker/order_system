from dataclasses import dataclass
from typing import Iterable

from fastapi import Depends, Header, HTTPException, status


ALLOWED_ROLES = {'admin', 'order_entry', 'buyer', 'supplier', 'customer'}


@dataclass
class AuthContext:
    user_id: str
    role: str
    supplier_id: int | None = None
    customer_id: int | None = None


def get_auth_context(
    x_user_id: str | None = Header(default=None),
    x_role: str | None = Header(default=None),
    x_supplier_id: int | None = Header(default=None),
    x_customer_id: int | None = Header(default=None),
) -> AuthContext:
    if not x_user_id or not x_role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='missing auth headers')

    role = x_role.strip().lower()
    if role not in ALLOWED_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='invalid role')

    return AuthContext(user_id=x_user_id, role=role, supplier_id=x_supplier_id, customer_id=x_customer_id)


def require_roles(*roles: str):
    allowed = {r.lower() for r in roles}

    def _dep(ctx: AuthContext = Depends(get_auth_context)) -> AuthContext:
        if ctx.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='forbidden')
        return ctx

    return _dep


def require_supplier_scope(target_supplier_id: int, ctx: AuthContext) -> None:
    if ctx.role == 'supplier' and ctx.supplier_id != target_supplier_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='supplier out of scope')


def require_customer_scope(target_customer_id: int, ctx: AuthContext) -> None:
    if ctx.role == 'customer' and ctx.customer_id != target_customer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='customer out of scope')
