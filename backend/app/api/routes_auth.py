from fastapi import APIRouter, Depends

from app.core.auth import (
    ALLOWED_ROLES,
    AuthContext,
    get_auth_context,
    issue_tokens,
    parse_refresh_token,
    revoke_refresh_token,
)
from app.core.errors import api_error
from app.schemas.auth import LoginRequest, MeResponse, TokenRefreshRequest, TokenResponse

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    role = payload.role.strip().lower()
    if role not in ALLOWED_ROLES:
        api_error(403, 'FORBIDDEN', 'forbidden')

    access, refresh, ttl = issue_tokens(user_id=payload.user_id, role=role)
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=ttl)


@router.post('/refresh', response_model=TokenResponse)
def refresh(payload: TokenRefreshRequest) -> TokenResponse:
    decoded = parse_refresh_token(payload.refresh_token)
    access, refresh_token, ttl = issue_tokens(user_id=decoded['sub'], role=decoded['role'])
    return TokenResponse(access_token=access, refresh_token=refresh_token, expires_in=ttl)


@router.post('/logout')
def logout(payload: TokenRefreshRequest):
    revoke_refresh_token(payload.refresh_token)
    return {'ok': True}


@router.get('/me', response_model=MeResponse)
def me(auth: AuthContext = Depends(get_auth_context)) -> MeResponse:
    return MeResponse(user_id=auth.user_id, role=auth.role)
