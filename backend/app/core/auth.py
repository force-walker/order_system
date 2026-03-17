from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import uuid

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.errors import api_error


ALLOWED_ROLES = {'admin', 'order_entry', 'buyer', 'supplier', 'customer'}
bearer = HTTPBearer(auto_error=False)
REVOKED_REFRESH_JTI: set[str] = set()


@dataclass
class AuthContext:
    user_id: str
    role: str
    supplier_id: int | None = None
    customer_id: int | None = None


def _encode(payload: dict) -> str:
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _decode(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError:
        api_error(401, 'AUTH_REQUIRED', 'token expired')
    except jwt.InvalidTokenError:
        api_error(401, 'AUTH_REQUIRED', 'invalid token')


def issue_tokens(user_id: str, role: str) -> tuple[str, str, int]:
    now = datetime.now(UTC)
    access_exp = now + timedelta(seconds=settings.jwt_access_ttl_seconds)
    refresh_exp = now + timedelta(seconds=settings.jwt_refresh_ttl_seconds)
    access = _encode(
        {
            'sub': user_id,
            'role': role,
            'type': 'access',
            'exp': int(access_exp.timestamp()),
            'iat': int(now.timestamp()),
            'jti': uuid.uuid4().hex,
        }
    )
    refresh = _encode(
        {
            'sub': user_id,
            'role': role,
            'type': 'refresh',
            'exp': int(refresh_exp.timestamp()),
            'iat': int(now.timestamp()),
            'jti': uuid.uuid4().hex,
        }
    )
    return access, refresh, settings.jwt_access_ttl_seconds


def parse_refresh_token(refresh_token: str) -> dict:
    payload = _decode(refresh_token)
    if payload.get('type') != 'refresh':
        api_error(401, 'AUTH_REQUIRED', 'invalid refresh token type')
    jti = payload.get('jti')
    if jti in REVOKED_REFRESH_JTI:
        api_error(401, 'AUTH_REQUIRED', 'refresh token revoked')
    return payload


def revoke_refresh_token(refresh_token: str) -> None:
    payload = _decode(refresh_token)
    if payload.get('type') == 'refresh' and payload.get('jti'):
        REVOKED_REFRESH_JTI.add(payload['jti'])


def get_auth_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> AuthContext:
    if not credentials or credentials.scheme.lower() != 'bearer':
        api_error(401, 'AUTH_REQUIRED', 'missing bearer token')

    payload = _decode(credentials.credentials)
    if payload.get('type') != 'access':
        api_error(401, 'AUTH_REQUIRED', 'invalid token type')

    role = str(payload.get('role', '')).strip().lower()
    user_id = payload.get('sub')
    if not user_id or role not in ALLOWED_ROLES:
        api_error(403, 'FORBIDDEN', 'forbidden')

    return AuthContext(user_id=user_id, role=role)


def require_roles(*roles: str):
    allowed = {r.lower() for r in roles}

    def _dep(ctx: AuthContext = Depends(get_auth_context)) -> AuthContext:
        if ctx.role not in allowed:
            api_error(403, 'FORBIDDEN', 'forbidden')
        return ctx

    return _dep


def require_supplier_scope(target_supplier_id: int, ctx: AuthContext) -> None:
    if ctx.role == 'supplier' and ctx.supplier_id != target_supplier_id:
        api_error(403, 'FORBIDDEN', 'supplier out of scope')


def require_customer_scope(target_customer_id: int, ctx: AuthContext) -> None:
    if ctx.role == 'customer' and ctx.customer_id != target_customer_id:
        api_error(403, 'FORBIDDEN', 'customer out of scope')
