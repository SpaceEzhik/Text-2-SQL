from fastapi import Depends, Response, Request, HTTPException, status, APIRouter

# from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db import db_helper_admin
from frontend.frontend import templates
from . import auth_prefix
from .exceptions import UnauthorizedException
from .helpers import (
    get_current_access_token_payload,
    get_current_refresh_token_payload,
    get_user_by_token_sub,
    delete_tokens,
    create_and_store_tokens,
)
from .validation import (
    validate_auth_user,
)
from schemas import UserSchema, TokenInfo

# http_bearer = HTTPBearer(auto_error=False)
router = APIRouter(
    prefix=auth_prefix,
    # dependencies=[Depends(http_bearer)],
)


@router.get("/login", response_model=TokenInfo)
async def auth_user_issue_jwt(
    request: Request,
):
    return templates.TemplateResponse(
        request,
        "login.html",
        {
            "login_url": request.url_for("auth_user_issue_jwt"),
            "redirect_url": settings.api.current_root_url,
        },
    )


@router.post("/login", response_model=TokenInfo)
async def auth_user_issue_jwt(
    response: Response,
    db_session: AsyncSession = Depends(db_helper_admin.session_dependency),
    user: UserSchema = Depends(validate_auth_user),
):
    access_token, refresh_token = await create_and_store_tokens(
        response,
        db_session,
        user=user,
    )
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
async def auth_user_logout(
    response: Response,
    db_session: AsyncSession = Depends(db_helper_admin.session_dependency),
    payload: dict = Depends(get_current_refresh_token_payload),
):
    user: UserSchema = await get_user_by_token_sub(payload, db_session)
    await delete_tokens(
        response,
        db_session,
        user=user,
    )
    return {"logout": "success"}


@router.post(
    "/refresh",
    response_model=TokenInfo,
    response_model_exclude_none=True,
)
async def auth_refresh_jwt(
    request: Request,
    response: Response,
    db_session: AsyncSession = Depends(db_helper_admin.session_dependency),
    payload: dict = Depends(get_current_refresh_token_payload),
):
    user: UserSchema = await get_user_by_token_sub(payload, db_session)
    print(user)
    if not (
        user.is_active and user.refresh_token == request.cookies.get("refresh_token")
    ):
        # raise HTTPException(
        #     status_code=status.HTTP_403_FORBIDDEN,
        #     detail="Пользователь деактивирован",
        # )
        raise UnauthorizedException("user deactivated, login required")
    access_token, refresh_token = await create_and_store_tokens(
        response,
        db_session,
        user=user,
    )
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.get("/users/me/")
async def auth_user_check_self_info(
    db_session: AsyncSession = Depends(db_helper_admin.session_dependency),
    payload: dict = Depends(get_current_access_token_payload),
):
    user: UserSchema = await get_user_by_token_sub(payload, db_session)
    iat = payload.get("iat")
    return {
        "email": user.email,
        "logged_in_at": iat,
    }
