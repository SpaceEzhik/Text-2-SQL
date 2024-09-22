from datetime import timedelta
from fastapi import Depends, HTTPException
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from config import settings
from db.crud import update_user_refresh_token, get_user_by_email
from db import db_helper_admin
from schemas import UserSchema
from security import utils as auth_utils
from security.utils import encode_jwt

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def create_jwt(
    token_type: str,
    token_data: dict,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


def create_access_token(user: UserSchema) -> str:
    jwt_payload = {
        # subject
        "sub": user.email,
        "user_group": user.user_group,
    }
    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )


def create_refresh_token(user: UserSchema) -> str:
    jwt_payload = {
        "sub": user.email,
    }
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
    )


async def store_tokens(
    response: Response,
    db_session: AsyncSession,
    access_token: str,
    refresh_token: str,
    user: UserSchema,
):
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    await update_user_refresh_token(db_session, token=refresh_token, email=user.email)


async def delete_tokens(
    response: Response,
    db_session: AsyncSession,
    user: UserSchema,
) -> None:
    response.delete_cookie(key="access_token", httponly=True)
    response.delete_cookie(key="refresh_token", httponly=True)
    await update_user_refresh_token(db_session, token=None, email=user.email)


async def create_and_store_tokens(
    response: Response,
    db_session: AsyncSession,
    user: UserSchema,
):
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    await store_tokens(
        response,
        db_session,
        access_token=access_token,
        refresh_token=refresh_token,
        user=user,
    )
    return access_token, refresh_token


def access_token_getter(request: Request) -> str | None:
    return request.cookies.get("access_token")


def refresh_token_getter(request: Request) -> str | None:
    return request.cookies.get("refresh_token")


def get_current_access_token_payload(
    token: str = Depends(access_token_getter),
) -> dict:
    try:
        payload = auth_utils.decode_jwt(
            token=token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Неправильный токен: {e}",
        )
    return payload


def get_current_refresh_token_payload(
    token: str = Depends(refresh_token_getter),
) -> dict:
    try:
        payload = auth_utils.decode_jwt(
            token=token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Неправильный токен: {e}",
        )
    return payload


async def get_user_by_token_sub(
    payload: dict,
    db_session: AsyncSession = Depends(db_helper_admin.session_dependency),
) -> UserSchema:
    email: str | None = payload.get("sub")

    user = await get_user_by_email(db_session, email)
    if user:
        return UserSchema.model_validate(user)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неправильный токен (пользователь не найден)",
    )


def get_user_group_from_token(
    payload: dict = Depends(get_current_access_token_payload),
):
    return payload["user_group"]
