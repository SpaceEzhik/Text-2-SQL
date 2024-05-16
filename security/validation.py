from typing import Literal

from fastapi import Depends, HTTPException, Form, status, Request
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import get_user_by_email
from db.db_helpers import db_helper_admin
from .helpers import (
    TOKEN_TYPE_FIELD,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
)
import security.utils as auth_utils
from schemas import UserSchema

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login/",
)


def refresh_token_getter(request: Request) -> str | None:
    return request.cookies.get("refresh_token")


def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
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
    request: Request,
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


# def get_current_token__payload_by_type(
#     request: Request,
#     token_type: Literal[ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE],
#     access_token: str = Depends(OAuth2PasswordBearer),
#     refresh_token: str = Depends(refresh_token_getter),
# ) -> dict:
#     payloads = {}
#     try:
#         payloads[ACCESS_TOKEN_TYPE] = auth_utils.decode_jwt(
#             token=access_token,
#         )
#         payloads[REFRESH_TOKEN_TYPE] = auth_utils.decode_jwt(
#             token=refresh_token,
#         )
#     except InvalidTokenError as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=f"Неправильный токен: {e}",
#         )
#     return payloads


def validate_token_type(
    payload: dict,
    token_type: str,
) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Неправильный тип токена {current_token_type!r}, ожидается {token_type!r}",
    )


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


async def validate_auth_user(
    username: str = Form(),  # actually its email in my app, but if I replace "username" with "email" - OAuth2 wouldn't work ¯\_(ツ)_/¯
    password: str = Form(),
    db_session: AsyncSession = Depends(db_helper_admin.session_dependency),
) -> UserSchema:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неправильная почта или пароль",
    )

    user = await get_user_by_email(db_session, username)
    if not user:
        raise unauthed_exc

    if not auth_utils.validate_password(
        password=password,
        hashed_password=user.password,
    ):
        raise unauthed_exc

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь деактивирован",
        )

    return UserSchema.model_validate(user)
