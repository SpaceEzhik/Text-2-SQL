from fastapi import APIRouter, Depends, Response, Request, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import update_user_refresh_token
from db.db_helpers import db_helper_admin
from frontend.frontend import templates
from .helpers import (
    create_access_token,
    create_refresh_token,
)
from .validation import (
    validate_auth_user,
    get_user_by_token_sub,
    get_current_token_payload,
    get_current_refresh_token_payload,
)
from schemas import UserSchema

http_bearer = HTTPBearer(auto_error=False)


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


router = APIRouter(
    prefix="/auth",
    dependencies=[Depends(http_bearer)],
)


@router.get("/login", response_model=TokenInfo)
async def auth_user_issue_jwt(
    request: Request,
):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "login_url": router.prefix + "/login",
            "redirect_url": "/",
        },
    )


@router.post("/login", response_model=TokenInfo)
async def auth_user_issue_jwt(
    response: Response,
    db_session: AsyncSession = Depends(db_helper_admin.session_dependency),
    user: UserSchema = Depends(validate_auth_user),
):
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    await update_user_refresh_token(db_session, token=refresh_token, email=user.email)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь деактивирован",
        )
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    await update_user_refresh_token(db_session, token=refresh_token, email=user.email)
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.get("/users/me/")
async def auth_user_check_self_info(
    db_session: AsyncSession = Depends(db_helper_admin.session_dependency),
    payload: dict = Depends(get_current_token_payload),
):
    user: UserSchema = await get_user_by_token_sub(payload, db_session)
    iat = payload.get("iat")
    return {
        "email": user.email,
        "logged_in_at": iat,
    }
